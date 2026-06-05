"""The modern SDK (IAppClient / AsyncIAppClient) hits the same verified endpoints."""

import base64

import httpx
import pytest
import respx

from iapp_ai import AsyncIAppClient, IAppClient, IAppError
from iapp_ai._core import API_BASE

JSON_OK = {"ok": True}
LLM_OK = {"choices": [{"message": {"content": "hi"}}]}
IMAGE_OK = {
    "candidates": [
        {"content": {"parts": [{"inlineData": {"data": base64.b64encode(b"png").decode()}}]}}
    ]
}


def build_specs(c, m):
    """(callable, method, exact path, mock json|bytes) per SDK method."""
    img, wav = m["img"], m["wav"]
    return {
        "ekyc.thai_id_card front": (lambda: c.ekyc.thai_id_card(img), "POST", "/v3/store/ekyc/thai-national-id-card/front", JSON_OK),
        "ekyc.thai_id_card back": (lambda: c.ekyc.thai_id_card(img, side="back"), "POST", "/v3/store/ekyc/thai-national-id-card/back", JSON_OK),
        "ekyc.thai_id_card_photocopy": (lambda: c.ekyc.thai_id_card_photocopy(img), "POST", "/v3/store/ekyc/thai-national-id-card-with-signature", JSON_OK),
        "ekyc.passport": (lambda: c.ekyc.passport(img), "POST", "/v3/store/ekyc/passport", JSON_OK),
        "ekyc.driver_license": (lambda: c.ekyc.driver_license(img), "POST", "/v3/store/ekyc/thai-driver-license", JSON_OK),
        "ekyc.book_bank": (lambda: c.ekyc.book_bank(img), "POST", "/v3/store/ekyc/book-bank", JSON_OK),
        "ekyc.face_verification": (lambda: c.ekyc.face_verification(img, img), "POST", "/v3/store/ekyc/face-verification", JSON_OK),
        "ekyc.face_detection single": (lambda: c.ekyc.face_detection(img), "POST", "/v3/store/ekyc/face-detection/single", JSON_OK),
        "ekyc.face_detection multi": (lambda: c.ekyc.face_detection(img, mode="multi"), "POST", "/v3/store/ekyc/face-detection/multi", JSON_OK),
        "ekyc.face_liveness": (lambda: c.ekyc.face_liveness(img), "POST", "/v3/store/ekyc/face-passive-liveness", JSON_OK),
        "ekyc.face_id_card_kyc": (lambda: c.ekyc.face_id_card_kyc(img, img), "POST", "/v3/store/ekyc/face-and-id-card-verification", JSON_OK),
        "ekyc.face_recognition add": (lambda: c.ekyc.face_recognition("add", "co", file_path=img, name="n", password="p"), "POST", "/v3/store/ekyc/face-recognition/add", JSON_OK),
        "ekyc.face_recognition check": (lambda: c.ekyc.face_recognition("check", "co", password="p"), "POST", "/v3/store/ekyc/face-recognition/check", JSON_OK),
        "ocr.document text": (lambda: c.ocr.document(img), "POST", "/v3/store/ocr/document/ocr", JSON_OK),
        "ocr.document layout": (lambda: c.ocr.document(img, mode="layout"), "POST", "/v3/store/ocr/document/layout", JSON_OK),
        "ocr.document docx": (lambda: c.ocr.document(img, mode="docx"), "POST", "/v3/store/ocr/document/docx", JSON_OK),
        "ocr.receipt": (lambda: c.ocr.receipt(img), "POST", "/ocr/v3/receipt/file", JSON_OK),
        "ocr.credit_card_statement": (lambda: c.ocr.credit_card_statement(img), "POST", "/ocr/v3/creditcard-statement/file", JSON_OK),
        "ocr.tax_deduction_certificate": (lambda: c.ocr.tax_deduction_certificate(img), "POST", "/ocr/v3/tax-deduction-certificate/file", JSON_OK),
        "ocr.civil_registration": (lambda: c.ocr.civil_registration(img), "POST", "/ocr/v3/civil-registeration-certificate/file", JSON_OK),
        "ocr.resume": (lambda: c.ocr.resume(img), "POST", "/v3/store/ocr/curriculum-vitae", JSON_OK),
        "ocr.job_description": (lambda: c.ocr.job_description(img), "POST", "/v3/store/ocr/job-description", JSON_OK),
        "llm.chat chinda": (lambda: c.llm.chat("hi"), "POST", "/v3/llm/chinda-thaillm-4b/chat/completions", LLM_OK),
        "llm.chat deepseek-v4": (lambda: c.llm.chat("hi", model="deepseek-v4-pro"), "POST", "/v3/llm/deepseek-v4/chat/completions", LLM_OK),
        "llm.thanoy_legal_qa": (lambda: c.llm.thanoy_legal_qa("q"), "POST", "/v3/store/llm/thanoy-legal-ai", JSON_OK),
        "nlp.translate": (lambda: c.nlp.translate("hi", "en", "th"), "POST", "/v1/text/translate", JSON_OK),
        "nlp.summarize": (lambda: c.nlp.summarize("t"), "POST", "/v3/store/nlp/thai-text-summary", JSON_OK),
        "nlp.sentiment": (lambda: c.nlp.sentiment("t"), "POST", "/v3/store/nlp/sentiment-analysis", JSON_OK),
        "nlp.toxicity": (lambda: c.nlp.toxicity("t"), "POST", "/v3/store/nlp/toxicity-classification", JSON_OK),
        "nlp.qa": (lambda: c.nlp.qa("q", "d"), "POST", "/thai-qa", JSON_OK),
        "nlp.question_generation": (lambda: c.nlp.question_generation("t"), "GET", "/v3/store/nlp/question/generation", JSON_OK),
        "speech.transcribe th base": (lambda: c.speech.transcribe(wav), "POST", "/v3/store/speech/speech-to-text/base", JSON_OK),
        "speech.transcribe zh pro": (lambda: c.speech.transcribe(wav, language="zh", quality="pro"), "POST", "/v3/store/speech/speech-to-text/pro/zh", JSON_OK),
        "speech.tts kaitom-v3": (lambda: c.speech.tts("t", m["out_wav"]), "POST", "/v3/store/audio/tts", b"\x00\x01" * 50),
        "speech.tts cee": (lambda: c.speech.tts("t", m["out_wav"], voice="cee"), "GET", "/v3/store/speech/text-to-speech/cee", b"RIFF"),
        "speech.voice_clone": (lambda: c.speech.voice_clone("t", wav, "r", m["out_wav"]), "POST", "/v3/store/audio/tts/clone", b"RIFF"),
        "speech.ai_audio_detection": (lambda: c.speech.ai_audio_detection(wav), "POST", "/v3/store/audio/tts/detect", JSON_OK),
        "image.generate": (lambda: c.image.generate("p", m["out_png"]), "POST", "/v3/image/generation/google/nanobanana/generate", IMAGE_OK),
        "image.generate pro": (lambda: c.image.generate("p", m["out_png"], model="nanobanana-pro"), "POST", "/v3/image/generation/google/nanobananapro/generate", IMAGE_OK),
        "image.remove_background": (lambda: c.image.remove_background(img, m["out_png"]), "POST", "/v3/store/smart-city/remove-background", b"\x89PNG"),
        "video.submit": (lambda: c.video.submit("p"), "POST", "/v3/store/video/seedance/tasks", JSON_OK),
        "video.status": (lambda: c.video.status("t1"), "GET", "/v3/store/video/seedance/tasks/t1", JSON_OK),
        "smartcity.license_plate": (lambda: c.smartcity.license_plate(img), "POST", "/v3/store/smart-city/license-plate-ocr", JSON_OK),
        "smartcity.meter": (lambda: c.smartcity.meter(img), "POST", "/v3/store/smart-city/power-meter-and-water-meter/file", JSON_OK),
        "smartcity.route_optimization": (lambda: c.smartcity.route_optimization("a", 13.7, 100.5, stops=[{"customerName": "A", "customerPhone": "08", "customerAddress": "BKK", "item": "box"}]), "POST", "/v3/store/smart-city/automatic-route-optimization", JSON_OK),
        "data.thai_holidays year": (lambda: c.data.thai_holidays(year=2026), "GET", "/v3/store/data/thai-holiday/year/2026", JSON_OK),
        "data.thai_holidays range": (lambda: c.data.thai_holidays(start_date="2026-01-01", end_date="2026-12-31"), "GET", "/v3/store/data/thai-holiday/range", JSON_OK),
        "data.thai_holidays default": (lambda: c.data.thai_holidays(), "GET", "/v3/store/data/thai-holiday", JSON_OK),
    }


SPEC_KEYS = sorted(
    build_specs(
        type("C", (), {"__getattr__": lambda self, _: self, "__call__": lambda self, *a, **k: None})(),
        {"img": "x", "wav": "x", "out_png": "x", "out_wav": "x"},
    )
)


def _mock_response(body):
    if isinstance(body, bytes):
        return httpx.Response(200, content=body)
    return httpx.Response(200, json=body)


@pytest.mark.parametrize("key", SPEC_KEYS)
def test_sync_client_hits_verified_endpoint(key, media):
    client = IAppClient(api_key="k")
    fn, method, path, body = build_specs(client, media)[key]
    with respx.mock(base_url=API_BASE) as router:
        route = router.route(method=method, path=path).mock(return_value=_mock_response(body))
        fn()
    assert route.called, f"{key} did not call {method} {path}"


@pytest.mark.parametrize("key", SPEC_KEYS)
async def test_async_client_hits_verified_endpoint(key, media):
    client = AsyncIAppClient(api_key="k")
    fn, method, path, body = build_specs(client, media)[key]
    with respx.mock(base_url=API_BASE) as router:
        route = router.route(method=method, path=path).mock(return_value=_mock_response(body))
        await fn()
    assert route.called, f"{key} did not call {method} {path}"


def test_sync_client_raises_iapp_error():
    client = IAppClient(api_key="k")
    with respx.mock(base_url=API_BASE) as router:
        router.post("/v3/store/nlp/sentiment-analysis").mock(return_value=httpx.Response(401))
        with pytest.raises(IAppError) as exc:
            client.nlp.sentiment("t")
    assert exc.value.status_code == 401


def test_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("IAPP_API_KEY", raising=False)
    with pytest.raises(IAppError, match="No API key"):
        IAppClient()


def test_client_reads_env_key(monkeypatch):
    monkeypatch.setenv("IAPP_API_KEY", "env-key")
    assert IAppClient().api_key == "env-key"


def test_tts_writes_wav(media):
    client = IAppClient(api_key="k")
    with respx.mock(base_url=API_BASE) as router:
        router.post("/v3/store/audio/tts").mock(return_value=httpx.Response(200, content=b"\x00\x01" * 100))
        path = client.speech.tts("สวัสดี", media["out_wav"])
    with open(path, "rb") as f:
        assert f.read(4) == b"RIFF"
