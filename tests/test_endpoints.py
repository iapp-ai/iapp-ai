"""Every tool must call the verified iApp endpoint (method + path + payload shape).

Endpoints were verified end-to-end against the live API (see internal notes).
HTTP here is fully mocked with respx — respx blocks any unmocked request, so a tool
that drifts to a wrong path or method fails its test immediately. This guards the
exact class of bug found during E2E (e.g. `/thai-text-summary/v2` and
`/ekyc/passport/v2` were documented but do not exist).
"""

import base64
import json

import httpx
import pytest
import respx

from iapp_mcp.client import API_BASE
from iapp_mcp.tools import ekyc, generation, llm, nlp, ocr, smartcity, speech
from iapp_mcp.tools.smartcity import RouteStop

JSON_OK = {"ok": True}
LLM_OK = {
    "choices": [{"message": {"content": "hello"}}],
    "usage": {"total_tokens": 3},
}
IMAGE_OK = {
    "candidates": [
        {
            "content": {
                "parts": [
                    {"inlineData": {"data": base64.b64encode(b"fake-png").decode()}}
                ]
            }
        }
    ]
}


def _stop(name):
    return RouteStop(
        customerName=name,
        customerPhone="0812345678",
        customerAddress="Bangkok",
        item="box",
        latitude=13.75,
        longitude=100.5,
    )


def build_specs(m):
    """Spec per case: (coroutine factory, method, exact path, mock json|bytes)."""
    img, wav = m["img"], m["wav"]
    return {
        # ── eKYC ────────────────────────────────────────────────────────────
        "id_card_front": (lambda: ekyc.iapp_thai_id_card_ocr(file_path=img), "POST", "/v3/store/ekyc/thai-national-id-card/front", JSON_OK),
        "id_card_back": (lambda: ekyc.iapp_thai_id_card_ocr(file_path=img, side="back"), "POST", "/v3/store/ekyc/thai-national-id-card/back", JSON_OK),
        "id_card_photocopy": (lambda: ekyc.iapp_thai_id_card_photocopy_ocr(file_path=img), "POST", "/v3/store/ekyc/thai-national-id-card-with-signature", JSON_OK),
        # /v2 suffix documented on the website does NOT exist — verified live.
        "passport": (lambda: ekyc.iapp_passport_ocr(file_path=img), "POST", "/v3/store/ekyc/passport", JSON_OK),
        "driver_license": (lambda: ekyc.iapp_thai_driver_license_ocr(file_path=img), "POST", "/v3/store/ekyc/thai-driver-license", JSON_OK),
        "book_bank": (lambda: ekyc.iapp_book_bank_ocr(file_path=img), "POST", "/v3/store/ekyc/book-bank", JSON_OK),
        "face_verification": (lambda: ekyc.iapp_face_verification(image1_path=img, image2_path=img), "POST", "/v3/store/ekyc/face-verification", JSON_OK),
        "face_detection_single": (lambda: ekyc.iapp_face_detection(file_path=img), "POST", "/v3/store/ekyc/face-detection/single", JSON_OK),
        "face_detection_multi": (lambda: ekyc.iapp_face_detection(file_path=img, mode="multi"), "POST", "/v3/store/ekyc/face-detection/multi", JSON_OK),
        "face_liveness": (lambda: ekyc.iapp_face_liveness(file_path=img), "POST", "/v3/store/ekyc/face-passive-liveness", JSON_OK),
        "face_id_card_kyc": (lambda: ekyc.iapp_face_id_card_kyc(id_card_path=img, selfie_path=img), "POST", "/v3/store/ekyc/face-and-id-card-verification", JSON_OK),
        "face_rec_single": (lambda: ekyc.iapp_face_recognition(action="recognize_single", company="c", file_path=img), "POST", "/v3/store/ekyc/face-recognition/single", JSON_OK),
        "face_rec_multi": (lambda: ekyc.iapp_face_recognition(action="recognize_multi", company="c", file_path=img), "POST", "/v3/store/ekyc/face-recognition/multi", JSON_OK),
        "face_rec_add": (lambda: ekyc.iapp_face_recognition(action="add", company="c", file_path=img, name="n", password="p"), "POST", "/v3/store/ekyc/face-recognition/add", JSON_OK),
        "face_rec_remove": (lambda: ekyc.iapp_face_recognition(action="remove", company="c", name="n", password="p"), "POST", "/v3/store/ekyc/face-recognition/remove", JSON_OK),
        "face_rec_check": (lambda: ekyc.iapp_face_recognition(action="check", company="c", password="p"), "POST", "/v3/store/ekyc/face-recognition/check", JSON_OK),
        # ── Document OCR ────────────────────────────────────────────────────
        "document_ocr_text": (lambda: ocr.iapp_document_ocr(file_path=img), "POST", "/v3/store/ocr/document/ocr", JSON_OK),
        "document_ocr_layout": (lambda: ocr.iapp_document_ocr(file_path=img, mode="layout"), "POST", "/v3/store/ocr/document/layout", JSON_OK),
        "document_ocr_docx": (lambda: ocr.iapp_document_ocr(file_path=img, mode="docx"), "POST", "/v3/store/ocr/document/docx", JSON_OK),
        "receipt": (lambda: ocr.iapp_receipt_ocr(file_path=img), "POST", "/ocr/v3/receipt/file", JSON_OK),
        "cc_statement": (lambda: ocr.iapp_credit_card_statement_ocr(file_path=img), "POST", "/ocr/v3/creditcard-statement/file", JSON_OK),
        "tax_deduction": (lambda: ocr.iapp_tax_deduction_certificate_ocr(file_path=img), "POST", "/ocr/v3/tax-deduction-certificate/file", JSON_OK),
        "civil_registration": (lambda: ocr.iapp_civil_registration_ocr(file_path=img), "POST", "/ocr/v3/civil-registeration-certificate/file", JSON_OK),
        "resume": (lambda: ocr.iapp_resume_ocr(file_path=img), "POST", "/v3/store/ocr/curriculum-vitae", JSON_OK),
        "job_description": (lambda: ocr.iapp_job_description_ocr(file_path=img), "POST", "/v3/store/ocr/job-description", JSON_OK),
        # ── LLM ─────────────────────────────────────────────────────────────
        "llm_chinda": (lambda: llm.iapp_llm_chat(prompt="hi"), "POST", "/v3/llm/chinda-thaillm-4b/chat/completions", LLM_OK),
        "llm_deepseek_chat": (lambda: llm.iapp_llm_chat(prompt="hi", model="deepseek-chat"), "POST", "/v3/llm/deepseek-3p2/chat/completions", LLM_OK),
        "llm_deepseek_reasoner": (lambda: llm.iapp_llm_chat(prompt="hi", model="deepseek-reasoner"), "POST", "/v3/llm/deepseek-3p2/chat/completions", LLM_OK),
        "llm_deepseek_v4_flash": (lambda: llm.iapp_llm_chat(prompt="hi", model="deepseek-v4-flash"), "POST", "/v3/llm/deepseek-v4/chat/completions", LLM_OK),
        "llm_deepseek_v4_pro": (lambda: llm.iapp_llm_chat(prompt="hi", model="deepseek-v4-pro"), "POST", "/v3/llm/deepseek-v4/chat/completions", LLM_OK),
        "thanoy": (lambda: llm.iapp_thanoy_legal_qa(query="q"), "POST", "/v3/store/llm/thanoy-legal-ai", JSON_OK),
        # ── NLP ─────────────────────────────────────────────────────────────
        "translate": (lambda: nlp.iapp_translate(text="hi", source_lang="en", target_lang="th"), "POST", "/v1/text/translate", JSON_OK),
        # /v2 suffix documented on the website does NOT exist — verified live.
        "summarize": (lambda: nlp.iapp_summarize(text="t"), "POST", "/v3/store/nlp/thai-text-summary", JSON_OK),
        "sentiment": (lambda: nlp.iapp_sentiment_analysis(text="t"), "POST", "/v3/store/nlp/sentiment-analysis", JSON_OK),
        "toxicity": (lambda: nlp.iapp_toxicity_classification(text="t"), "POST", "/v3/store/nlp/toxicity-classification", JSON_OK),
        "thai_qa": (lambda: nlp.iapp_thai_qa(question="q", document="d"), "POST", "/thai-qa", JSON_OK),
        # Must be GET with a query param — POST returns 405, verified live.
        "question_generation": (lambda: nlp.iapp_question_generation(text="t"), "GET", "/v3/store/nlp/question/generation", JSON_OK),
        # ── Speech ──────────────────────────────────────────────────────────
        "stt_th_base": (lambda: speech.iapp_speech_to_text(file_path=wav), "POST", "/v3/store/speech/speech-to-text/base", JSON_OK),
        "stt_th_pro": (lambda: speech.iapp_speech_to_text(file_path=wav, quality="pro"), "POST", "/v3/store/speech/speech-to-text/pro", JSON_OK),
        "stt_en_base": (lambda: speech.iapp_speech_to_text(file_path=wav, language="en"), "POST", "/v3/store/speech/speech-to-text/base/en", JSON_OK),
        "stt_en_pro": (lambda: speech.iapp_speech_to_text(file_path=wav, language="en", quality="pro"), "POST", "/v3/store/speech/speech-to-text/pro/en", JSON_OK),
        "stt_zh_base": (lambda: speech.iapp_speech_to_text(file_path=wav, language="zh"), "POST", "/v3/store/speech/speech-to-text/base/zh", JSON_OK),
        "stt_zh_pro": (lambda: speech.iapp_speech_to_text(file_path=wav, language="zh", quality="pro"), "POST", "/v3/store/speech/speech-to-text/pro/zh", JSON_OK),
        "tts_kaitom_v3": (lambda: speech.iapp_text_to_speech(text="t", output_path=m["out_wav"]), "POST", "/v3/store/audio/tts", b"\x00\x01" * 100),
        "tts_kaitom_v2": (lambda: speech.iapp_text_to_speech(text="t", output_path=m["out_wav"], voice="kaitom-v2"), "POST", "/v3/store/speech/text-to-speech/kaitom", b"RIFFwav"),
        "tts_kaitom_v1": (lambda: speech.iapp_text_to_speech(text="t", output_path=m["out_mp3"], voice="kaitom-v1"), "GET", "/v3/store/speech/text-to-speech/kaitom/v1", b"ID3mp3"),
        "tts_cee": (lambda: speech.iapp_text_to_speech(text="t", output_path=m["out_wav"], voice="cee"), "GET", "/v3/store/speech/text-to-speech/cee", b"RIFFwav"),
        "voice_clone": (lambda: speech.iapp_voice_clone_tts(text="t", ref_audio_path=wav, ref_text="r", output_path=m["out_wav"]), "POST", "/v3/store/audio/tts/clone", b"RIFFwav"),
        "audio_detection": (lambda: speech.iapp_ai_audio_detection(audio_path=wav), "POST", "/v3/store/audio/tts/detect", JSON_OK),
        # ── Image / Video generation ────────────────────────────────────────
        "image_gen_nanobanana": (lambda: generation.iapp_image_generation(prompt="p", output_path=m["out_png"]), "POST", "/v3/image/generation/google/nanobanana/generate", IMAGE_OK),
        # Docs show /v3/image/image/... (typo, 404) — the real path verified live:
        "image_gen_nanobanana_pro": (lambda: generation.iapp_image_generation(prompt="p", output_path=m["out_png"], model="nanobanana-pro"), "POST", "/v3/image/generation/google/nanobananapro/generate", IMAGE_OK),
        "remove_background": (lambda: generation.iapp_remove_background(file_path=img, output_path=m["out_png"]), "POST", "/v3/store/smart-city/remove-background", b"\x89PNGfake"),
        "video_submit": (lambda: generation.iapp_video_generation_submit(prompt="p"), "POST", "/v3/store/video/seedance/tasks", JSON_OK),
        "video_status": (lambda: generation.iapp_video_generation_status(task_id="task-1"), "GET", "/v3/store/video/seedance/tasks/task-1", JSON_OK),
        # ── Smart City / Data ───────────────────────────────────────────────
        "license_plate": (lambda: smartcity.iapp_license_plate_ocr(file_path=img), "POST", "/v3/store/smart-city/license-plate-ocr", JSON_OK),
        "meter": (lambda: smartcity.iapp_meter_ocr(file_path=img), "POST", "/v3/store/smart-city/power-meter-and-water-meter/file", JSON_OK),
        "route_optimization": (lambda: smartcity.iapp_route_optimization(origin_address="a", origin_latitude=13.7, origin_longitude=100.5, stops=[_stop("A"), _stop("B")]), "POST", "/v3/store/smart-city/automatic-route-optimization", JSON_OK),
        "holidays_year": (lambda: smartcity.iapp_thai_holidays(year=2026), "GET", "/v3/store/data/thai-holiday/year/2026", JSON_OK),
        "holidays_range": (lambda: smartcity.iapp_thai_holidays(start_date="2026-01-01", end_date="2026-12-31"), "GET", "/v3/store/data/thai-holiday/range", JSON_OK),
        "holidays_default": (lambda: smartcity.iapp_thai_holidays(), "GET", "/v3/store/data/thai-holiday", JSON_OK),
    }


SPEC_KEYS = sorted(build_specs({"img": "x", "wav": "x", "out_png": "x", "out_wav": "x", "out_mp3": "x"}))


@pytest.mark.parametrize("key", SPEC_KEYS)
async def test_tool_calls_verified_endpoint(key, media):
    fn, method, path, mock_body = build_specs(media)[key]
    if isinstance(mock_body, bytes):
        mock_response = httpx.Response(200, content=mock_body)
    else:
        mock_response = httpx.Response(200, json=mock_body)

    # respx blocks unmocked requests, so a wrong method/path fails loudly.
    with respx.mock(base_url=API_BASE) as router:
        route = router.route(method=method, path=path).mock(return_value=mock_response)
        result = await fn()

    assert route.called, f"{key} did not call {method} {path}"
    assert not str(result).startswith("Error"), f"{key} returned an error: {str(result)[:200]}"


# ── payload-shape details that live probing proved matter ───────────────────


async def test_llm_chat_is_non_streaming(media):
    with respx.mock(base_url=API_BASE) as router:
        route = router.post("/v3/llm/chinda-thaillm-4b/chat/completions").mock(
            return_value=httpx.Response(200, json=LLM_OK)
        )
        await llm.iapp_llm_chat(prompt="hi")
    body = json.loads(route.calls.last.request.content)
    assert body["stream"] is False
    assert body["messages"][-1] == {"role": "user", "content": "hi"}


async def test_question_generation_uses_query_param():
    with respx.mock(base_url=API_BASE) as router:
        route = router.get("/v3/store/nlp/question/generation").mock(
            return_value=httpx.Response(200, json=JSON_OK)
        )
        await nlp.iapp_question_generation(text="กรุงเทพ")
    assert route.calls.last.request.url.params["text"] == "กรุงเทพ"


async def test_stt_pro_sends_asr_pro_flag(media):
    with respx.mock(base_url=API_BASE) as router:
        route = router.post("/v3/store/speech/speech-to-text/pro").mock(
            return_value=httpx.Response(200, json=JSON_OK)
        )
        await speech.iapp_speech_to_text(file_path=media["wav"], quality="pro")
    assert b"use_asr_pro" in route.calls.last.request.content


async def test_video_submit_maps_model_names():
    with respx.mock(base_url=API_BASE) as router:
        route = router.post("/v3/store/video/seedance/tasks").mock(
            return_value=httpx.Response(200, json=JSON_OK)
        )
        await generation.iapp_video_generation_submit(prompt="p", model="seedance-fast")
    body = json.loads(route.calls.last.request.content)
    assert body["model"] == "dreamina-seedance-2-0-fast-260128"


async def test_image_generation_saves_decoded_image(media):
    with respx.mock(base_url=API_BASE) as router:
        router.post("/v3/image/generation/google/nanobanana/generate").mock(
            return_value=httpx.Response(200, json=IMAGE_OK)
        )
        result = await generation.iapp_image_generation(prompt="p", output_path=media["out_png"])
    assert "Image saved" in result
    with open(media["out_png"], "rb") as f:
        assert f.read() == b"fake-png"
