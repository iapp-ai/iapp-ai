"""The MCP server boots and exposes all 37 tools with valid schemas."""

import iapp_mcp.server  # noqa: F401 — importing registers every tool module
from iapp_mcp.app import mcp

EXPECTED_TOOLS = {
    # eKYC
    "iapp_thai_id_card_ocr",
    "iapp_thai_id_card_photocopy_ocr",
    "iapp_passport_ocr",
    "iapp_thai_driver_license_ocr",
    "iapp_book_bank_ocr",
    "iapp_face_verification",
    "iapp_face_detection",
    "iapp_face_liveness",
    "iapp_face_id_card_kyc",
    "iapp_face_recognition",
    # Document OCR
    "iapp_document_ocr",
    "iapp_receipt_ocr",
    "iapp_credit_card_statement_ocr",
    "iapp_tax_deduction_certificate_ocr",
    "iapp_civil_registration_ocr",
    "iapp_resume_ocr",
    "iapp_job_description_ocr",
    # LLM
    "iapp_llm_chat",
    "iapp_thanoy_legal_qa",
    # NLP
    "iapp_translate",
    "iapp_summarize",
    "iapp_sentiment_analysis",
    "iapp_toxicity_classification",
    "iapp_thai_qa",
    "iapp_question_generation",
    # Speech
    "iapp_speech_to_text",
    "iapp_text_to_speech",
    "iapp_voice_clone_tts",
    "iapp_ai_audio_detection",
    # Image / Video generation
    "iapp_image_generation",
    "iapp_remove_background",
    "iapp_video_generation_submit",
    "iapp_video_generation_status",
    # Smart City / Data
    "iapp_license_plate_ocr",
    "iapp_meter_ocr",
    "iapp_route_optimization",
    "iapp_thai_holidays",
}


async def test_all_tools_registered():
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert names == EXPECTED_TOOLS
    assert len(tools) == 37


async def test_every_tool_has_description_and_schema():
    tools = await mcp.list_tools()
    for tool in tools:
        assert tool.description, f"{tool.name} has no description"
        assert tool.inputSchema.get("type") == "object", f"{tool.name} has no input schema"
