"""Shared fixtures: fake API key and dummy media files (all HTTP is mocked)."""

import pytest


@pytest.fixture(autouse=True)
def api_key_env(monkeypatch):
    """Every test runs with a fake API key set."""
    monkeypatch.setenv("IAPP_API_KEY", "test-key")


@pytest.fixture
def media(tmp_path):
    """Dummy input files + output paths. Content is irrelevant — HTTP is mocked."""
    img = tmp_path / "image.jpg"
    img.write_bytes(b"\xff\xd8\xff\xe0fake-jpeg")
    wav = tmp_path / "audio.wav"
    wav.write_bytes(b"RIFFfake-wav")
    return {
        "img": str(img),
        "wav": str(wav),
        "out_png": str(tmp_path / "out.png"),
        "out_wav": str(tmp_path / "out.wav"),
        "out_mp3": str(tmp_path / "out.mp3"),
    }
