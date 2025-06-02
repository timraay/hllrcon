import pytest
from hllrcon.protocol.request import RconRequest


def test_rconrequest_init_sets_fields() -> None:
    req = RconRequest("mycmd", 2, "token123", {"foo": "bar"})
    assert req.name == "mycmd"
    assert req.version == 2
    assert req.auth_token == "token123"
    assert req.content_body == {"foo": "bar"}
    assert isinstance(req.request_id, int)


def test_rconrequest_id_is_unique() -> None:
    req1 = RconRequest("cmd1", 1, None)
    req2 = RconRequest("cmd2", 1, None)
    assert req1.request_id != req2.request_id


def test_pack_with_dict_body_no_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("hllrcon.protocol.request.DO_USE_REQUEST_HEADERS", False)
    req = RconRequest("cmd", 1, "tok", {"a": 1})
    packed = req.pack()
    expected = (
        b'{"authToken":"tok","version":1,"name":"cmd","contentBody":"{\\"a\\":1}"}'
    )
    assert packed == expected


def test_pack_with_str_body_no_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("hllrcon.protocol.request.DO_USE_REQUEST_HEADERS", False)
    req = RconRequest("cmd", 1, "tok", "body")
    packed = req.pack()
    expected = b'{"authToken":"tok","version":1,"name":"cmd","contentBody":"body"}'
    assert packed == expected


def test_pack_with_none_auth_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("hllrcon.protocol.request.DO_USE_REQUEST_HEADERS", False)
    req = RconRequest("cmd", 1, None, "body")
    packed = req.pack()
    expected = b'{"authToken":"","version":1,"name":"cmd","contentBody":"body"}'
    assert packed == expected


def test_pack_with_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("hllrcon.protocol.request.DO_USE_REQUEST_HEADERS", True)
    req = RconRequest("cmd", 1, "tok", {"z": 9})
    packed = req.pack()

    expected_body = (
        b'{"authToken":"tok","version":1,"name":"cmd","contentBody":"{\\"z\\":9}"}'
    )
    expected = (
        req.request_id.to_bytes(4, byteorder="big")
        + len(expected_body).to_bytes(4, byteorder="big")
        + expected_body
    )
    assert packed == expected
