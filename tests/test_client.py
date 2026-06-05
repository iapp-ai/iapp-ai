"""Unit tests for client helpers: auth, error mapping, blob truncation, audio saving."""

import wave

import httpx
import pytest
import respx

from iapp_mcp.client import (
    API_BASE,
    IAppAPIError,
    _truncate_blobs,
    format_json_response,
    get_api_key,
    request,
    resolve_input_file,
    save_pcm_as_wav,
)


def test_get_api_key_missing(monkeypatch):
    monkeypatch.delenv("IAPP_API_KEY", raising=False)
    with pytest.raises(IAppAPIError, match="IAPP_API_KEY"):
        get_api_key()


def test_resolve_input_file_missing():
    with pytest.raises(IAppAPIError, match="not found"):
        resolve_input_file("/nonexistent/file.jpg")


def test_truncate_blobs_long_base64_is_truncated():
    blob = "QUJD" * 1000  # > 2048 chars of base64-looking data
    out = _truncate_blobs({"face": blob, "nested": [{"img": blob}]})
    assert "omitted" in out["face"]
    assert "omitted" in out["nested"][0]["img"]


def test_truncate_blobs_keeps_normal_strings():
    value = {"text": "สวัสดีครับ " * 500}  # long but not base64-looking
    assert _truncate_blobs(value) == value


def test_format_json_response_non_json_returns_raw_text():
    response = httpx.Response(200, text="not json")
    assert format_json_response(response) == "not json"


def test_save_pcm_as_wav(tmp_path):
    out = tmp_path / "audio.wav"
    pcm = b"\x00\x01" * 1200
    path = save_pcm_as_wav(pcm, str(out))
    with wave.open(path, "rb") as f:
        assert f.getnchannels() == 1
        assert f.getsampwidth() == 2
        assert f.getframerate() == 24000
        assert f.getnframes() == 1200


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (401, "Authentication failed"),
        (402, "Insufficient credits"),
        (413, "File too large"),
        (429, "Rate limit exceeded"),
        (500, "status 500"),
    ],
)
async def test_request_maps_http_errors(status, expected):
    with respx.mock(base_url=API_BASE) as router:
        router.post("/test").mock(return_value=httpx.Response(status, text="boom"))
        with pytest.raises(IAppAPIError, match=expected):
            await request("POST", "/test")


async def test_request_sends_apikey_header():
    with respx.mock(base_url=API_BASE) as router:
        route = router.get("/test").mock(return_value=httpx.Response(200, json={}))
        await request("GET", "/test")
    assert route.calls.last.request.headers["apikey"] == "test-key"
