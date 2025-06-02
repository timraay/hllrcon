import asyncio
from typing import Any
from unittest import mock

import pytest
from hllrcon.pooled.rcon import PooledRcon
from hllrcon.pooled.worker import PooledRconWorker
from pytest_mock import MockerFixture


@pytest.fixture
def pool(mocker: MockerFixture) -> PooledRcon:
    def worker_factory(*_args: Any, **_kwargs: dict[str, Any]) -> mock.Mock:  # noqa: ANN401
        mock_worker = mock.Mock(PooledRconWorker)
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
        pool_size=2,
    )


@pytest.mark.asyncio
async def test_get_worker_empty_pool(pool: PooledRcon) -> None:
    async with pool._get_available_worker():
        assert len(pool.workers) == 1
        assert pool._queue.empty()

    assert len(pool.workers) == 1
    assert pool._queue.qsize() == 1


@pytest.mark.asyncio
async def test_get_worker_one_available(pool: PooledRcon) -> None:
    async with pool._get_available_worker() as worker1:
        pass

    async with pool._get_available_worker() as worker2:
        assert worker1 is worker2
        assert len(pool.workers) == 1
        assert pool._queue.qsize() == 0

    assert len(pool.workers) == 1
    assert pool._queue.qsize() == 1


@pytest.mark.asyncio
async def test_get_worker_add_new(pool: PooledRcon) -> None:
    async with (
        pool._get_available_worker() as worker1,
        pool._get_available_worker() as worker2,
    ):
        assert worker1 is not worker2
        assert len(pool.workers) == 2
        assert pool._queue.qsize() == 0

    assert len(pool.workers) == 2
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
        pool.workers.remove(worker2)

        async with asyncio.timeout(0.1):
            async with pool._get_available_worker() as worker3:
                assert worker2 is not worker3


def test_pool_size_too_small() -> None:
    with pytest.raises(ValueError, match="Pool size must be greater than 0"):
        PooledRcon(host="localhost", port=1234, password="password", pool_size=0)

    with pytest.raises(ValueError, match="Pool size must be greater than 0"):
        PooledRcon(host="localhost", port=1234, password="password", pool_size=-1)


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
