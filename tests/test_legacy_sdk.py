"""The legacy v1.x SDK (`from iapp_ai import api`) must keep working in v2."""

import inspect

import iapp_ai
from iapp_ai import api

# Public methods present in v1.4.0 — removing any of these breaks SDK users.
V1_METHODS = {
    "thai_qa_api",
    "thai_qgen_api",
    "thai_text_summarization",
    "eng_thai_translate",
    "idcard_front",
    "idcard_front_photocopied",
    "idcard_back",
    "license_plate_ocr",
    "license_plate_base64",
    "book_bank_api",
    "passport_ocr",
    "document_ocr_plaintext",
    "document_ocr_json_layout",
    "document_ocr_docx",
    "face_liveness",
    "info_face_liveness",
    "power_meter",
    "water_meter_binary",
    "water_meter_base64",
    "face_verification",
    "face_ver_config_score",
    "face_ver2",
    "face_detect_single",
    "face_detect_multi",
    "face_detect_config_score",
    "face_recog_single",
    "face_recog_multi",
    "face_recog_facecrop",
    "face_recog_add",
    "face_recog_import",
    "face_recog_check",
    "face_recog_export",
    "face_recog_remove",
    "face_recog_config_score",
    "img_bg_removal_base64",
    "img_bg_removal_file",
    "driver_card_ocr",
    "thai_asr_api",
    "thai_thaitts_kaitom",
    "thai_thaitts_cee",
}


def test_legacy_import_and_constructor():
    client = api("test-key")
    assert client.apikey == "test-key"


def test_legacy_version_bumped():
    assert iapp_ai.__version__ == "2.0.0"


def test_all_v1_methods_still_exist():
    methods = {
        name
        for name, member in inspect.getmembers(api, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    missing = V1_METHODS - methods
    assert not missing, f"v1.4.0 SDK methods missing in v2: {sorted(missing)}"
