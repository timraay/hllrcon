import asyncio
import contextlib
from typing import Any
from unittest import mock

import pytest
from hllrcon.exceptions import HLLError
from hllrcon.pooled.rcon import PooledRcon
from hllrcon.pooled.worker import PooledRconWorker
from pytest_mock import MockerFixture


@pytest.fixture
def pool(mocker: MockerFixture) -> PooledRcon:
    def worker_factory(*_args: Any, **_kwargs: dict[str, Any]) -> mock.Mock:  # noqa: ANN401
        mock_worker = mock.Mock(PooledRconWorker)
        mock_worker.is_connected.return_value = True
        mock_worker.is_disconnected.return_value = False
        return mock_worker

    mocker.patch(
        "hllrcon.pooled.rcon.PooledRconWorker",
        side_effect=worker_factory,
    )

    return PooledRcon(
        host="localhost",
        port=1234,
        password="password",
        max_workers=2,
    )


@pytest.mark.asyncio
async def test_get_worker_empty_pool(pool: PooledRcon) -> None:
    async with pool._get_available_worker():
        assert len(pool._workers) == 1
        assert pool._queue.empty()

    assert len(pool._workers) == 1
    assert pool._queue.qsize() == 1


@pytest.mark.asyncio
async def test_get_worker_one_available(pool: PooledRcon) -> None:
    async with pool._get_available_worker() as worker1:
        pass

    async with pool._get_available_worker() as worker2:
        assert worker1 is worker2
        assert len(pool._workers) == 1
        assert pool._queue.qsize() == 0

    assert len(pool._workers) == 1
    assert pool._queue.qsize() == 1


@pytest.mark.asyncio
async def test_get_worker_add_new(pool: PooledRcon) -> None:
    async with (
        pool._get_available_worker() as worker1,
        pool._get_available_worker() as worker2,
    ):
        assert worker1 is not worker2
        assert len(pool._workers) == 2
        assert pool._queue.qsize() == 0

    assert len(pool._workers) == 2
    assert pool._queue.qsize() == 2


@pytest.mark.asyncio
async def test_get_worker_wait(pool: PooledRcon) -> None:
    async with pool._get_available_worker():
        async with pool._get_available_worker() as worker2:
            with pytest.raises(asyncio.TimeoutError):
                async with asyncio.timeout(0.1):
                    async with pool._get_available_worker():
                        pass

        async with asyncio.timeout(0.1):
            async with pool._get_available_worker() as worker3:
                assert worker2 is worker3


@pytest.mark.asyncio
async def test_get_worker_replace_disconnected(pool: PooledRcon) -> None:
    async with pool._get_available_worker():
        async with pool._get_available_worker() as worker2:
            pass

        worker2.is_disconnected.return_value = True  # type: ignore[attr-defined]
        pool._workers.remove(worker2)

        async with asyncio.timeout(0.1):
            async with pool._get_available_worker() as worker3:
                assert worker2 is not worker3


@pytest.mark.parametrize("max_workers", [0, -1])
def test_max_workers_too_small(max_workers: int) -> None:
    with pytest.raises(ValueError, match="Max workers must be greater than 0"):
        PooledRcon(
            host="localhost",
            port=1234,
            password="password",
            max_workers=max_workers,
        )


@pytest.mark.asyncio
async def test_is_connected(pool: PooledRcon) -> None:
    assert pool.is_connected() is False, "Pool should not be connected initially"

    async with pool._get_available_worker():
        assert pool.is_connected() is True

    assert pool.is_connected() is True

    pool.disconnect()
    assert pool.is_connected() is False, "Pool should not be connected after disconnect"


@pytest.mark.asyncio
async def test_num_workers(pool: PooledRcon) -> None:
    assert pool.num_workers == 0, "Pool should have no workers initially"

    async with pool._get_available_worker():
        assert pool.num_workers == 1

        async with pool._get_available_worker():
            assert pool.num_workers == 2

    assert pool.num_workers == 2

    pool.disconnect()
    assert pool.num_workers == 0


@pytest.mark.asyncio
async def test_execute(pool: PooledRcon) -> None:
    command = "command"
    version = 1
    body = "body"

    async with pool._get_available_worker() as worker:
        worker.execute = mock.AsyncMock(return_value="result")  # type: ignore[method-assign]

    result = await pool.execute(command, version, body)

    worker.execute.assert_called_once_with(command, version, body)
    assert result == "result"


@pytest.mark.asyncio
async def test_enter_exit(pool: PooledRcon) -> None:
    async with pool.connect(), pool._get_available_worker() as worker:
        assert pool._workers == [worker], "Worker should be added to the pool"

    assert not pool._workers, "Workers should be cleared after exit"
    assert pool._queue.empty(), "Queue should be empty after exit"

    with contextlib.suppress(RuntimeError):
        async with pool.connect(), pool._get_available_worker() as worker:
            assert pool._workers == [worker], "Worker should be added to the pool again"

            # Raise error this time
            raise RuntimeError

    assert not pool._workers, "Workers should be cleared after error"
    assert pool._queue.empty(), "Queue should be empty after error"


@pytest.mark.asyncio
async def test_wait_until_connected(pool: PooledRcon) -> None:
    assert not pool.is_connected(), "Pool should not be connected initially"

    await pool.wait_until_connected()
    assert pool.is_connected(), "Pool should be connected after waiting"
    assert pool.num_workers == 1, "Pool should have one worker after waiting"

    # Test connected worker
    await pool.wait_until_connected()

    worker = pool._workers[0]

    # Test connecting worker
    worker.is_connected.return_value = False  # type: ignore[attr-defined]
    worker.wait_until_connected = mock.AsyncMock()  # type: ignore[method-assign]
    await pool.wait_until_connected()
    worker.wait_until_connected.assert_awaited_once()

    # Test disconnected worker
    worker.is_disconnected.return_value = True  # type: ignore[attr-defined]
    worker.wait_until_connected.side_effect = HLLError
    await pool.wait_until_connected()
