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


def test_pack_with_header() -> None:
    req = RconRequest("cmd", 1, "tok", {"z": 9})
    packed = req.pack()

    expected_body = (
        b'{"authToken":"tok","version":1,"name":"cmd","contentBody":"{\\"z\\":9}"}'
    )
    expected_header = req.request_id.to_bytes(4, byteorder="little") + len(
        expected_body,
    ).to_bytes(4, byteorder="little")
    assert packed[0] == expected_header
    assert packed[1] == expected_body
