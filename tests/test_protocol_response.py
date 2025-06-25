import json

import pytest
from hllrcon.exceptions import HLLCommandError
from hllrcon.protocol.response import RconResponse, RconResponseStatus


def make_response(
    status_code: RconResponseStatus = RconResponseStatus.OK,
    content_body: str = '{"foo": "bar"}',
    status_message: str = "Success",
) -> RconResponse:
    return RconResponse(
        request_id=1,
        command="test",
        version=1,
        status_code=status_code,
        status_message=status_message,
        content_body=content_body,
    )


def test_rconresponse_init_sets_fields() -> None:
    resp = make_response()
    assert resp.request_id == 1
    assert resp.name == "test"
    assert resp.version == 1
    assert resp.status_code == RconResponseStatus.OK
    assert resp.status_message == "Success"
    assert resp.content_body == '{"foo": "bar"}'


def test_content_dict_valid_json() -> None:
    resp = make_response(content_body='{"a": 1, "b": 2}')
    assert resp.content_dict == {"a": 1, "b": 2}


def test_content_dict_invalid_json() -> None:
    resp = make_response(content_body="not json")
    with pytest.raises(json.JSONDecodeError):
        _ = resp.content_dict


def test_content_dict_not_a_dict() -> None:
    resp = make_response(content_body='["not a dict"]')
    with pytest.raises(TypeError, match="Expected JSON content to be a dict"):
        _ = resp.content_dict


def test_str_with_valid_json() -> None:
    resp = make_response(content_body='{"x": 42}')
    s = str(resp)
    assert "200" in s
    assert "test" in s
    assert "'x': 42" in s or '"x": 42' in s


def test_str_with_invalid_json() -> None:
    resp = make_response(content_body="not json")
    s = str(resp)
    assert "200" in s
    assert "test" in s
    assert "not json" in s


def test_unpack_returns_correct_instance() -> None:
    body = {
        "name": "cmd",
        "version": 2,
        "statusCode": 400,
        "statusMessage": "Bad request",
        "contentBody": '{"err": "fail"}',
    }
    body_encoded = json.dumps(body).encode()
    resp = RconResponse.unpack(99, body_encoded)
    assert resp.request_id == 99
    assert resp.name == "cmd"
    assert resp.version == 2
    assert resp.status_code == RconResponseStatus.BAD_REQUEST
    assert resp.status_message == "Bad request"
    assert resp.content_body == '{"err": "fail"}'


def test_raise_for_status_ok_does_not_raise() -> None:
    resp = make_response(status_code=RconResponseStatus.OK)
    resp.raise_for_status()  # Should not raise


@pytest.mark.parametrize(
    "code",
    [
        RconResponseStatus.BAD_REQUEST,
        RconResponseStatus.UNAUTHORIZED,
        RconResponseStatus.INTERNAL_ERROR,
    ],
)
def test_raise_for_status_raises(code: RconResponseStatus) -> None:
    resp = make_response(status_code=code, status_message="fail")
    with pytest.raises(HLLCommandError) as excinfo:
        resp.raise_for_status()
    assert excinfo.value.status_code == code
    assert str(excinfo.value) == f"({code}) fail"
