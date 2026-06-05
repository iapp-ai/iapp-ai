"""Core plumbing for the modern iApp AI SDK (shared by sync and async clients).

Namespace classes below define every API method exactly once. Each method body is
``return self._c._call(...)`` — on the sync client ``_call`` executes the request
and returns the result; on the async client ``_call`` is a coroutine function, so
the same method returns an awaitable. All endpoints were verified end-to-end
against the live API (2026-06).
"""

import base64
import json
import os
import wave
from typing import Any, Dict, List, Optional, Tuple

import httpx

API_BASE = "https://api.iapp.co.th"
TIMEOUT = httpx.Timeout(300.0, connect=15.0)

_STT_ENDPOINTS = {
    ("th", "base"): "/v3/store/speech/speech-to-text/base",
    ("th", "pro"): "/v3/store/speech/speech-to-text/pro",
    ("en", "base"): "/v3/store/speech/speech-to-text/base/en",
    ("en", "pro"): "/v3/store/speech/speech-to-text/pro/en",
    ("zh", "base"): "/v3/store/speech/speech-to-text/base/zh",
    ("zh", "pro"): "/v3/store/speech/speech-to-text/pro/zh",
}

_LLM_ENDPOINTS = {
    "chinda-qwen3-4b": "/v3/llm/chinda-thaillm-4b/chat/completions",
    "deepseek-reasoner": "/v3/llm/deepseek-3p2/chat/completions",
    "deepseek-chat": "/v3/llm/deepseek-3p2/chat/completions",
    "deepseek-v4-flash": "/v3/llm/deepseek-v4/chat/completions",
    "deepseek-v4-pro": "/v3/llm/deepseek-v4/chat/completions",
}

_VIDEO_MODELS = {
    "seedance": "dreamina-seedance-2-0-260128",
    "seedance-fast": "dreamina-seedance-2-0-fast-260128",
}

_FACE_RECOGNITION_ENDPOINTS = {
    "recognize_single": "/v3/store/ekyc/face-recognition/single",
    "recognize_multi": "/v3/store/ekyc/face-recognition/multi",
    "add": "/v3/store/ekyc/face-recognition/add",
    "remove": "/v3/store/ekyc/face-recognition/remove",
    "check": "/v3/store/ekyc/face-recognition/check",
}


class IAppError(Exception):
    """Raised when the iApp API returns an error response."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_text: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


def resolve_api_key(api_key: Optional[str]) -> str:
    key = (api_key or os.environ.get("IAPP_API_KEY", "")).strip()
    if not key:
        raise IAppError(
            "No API key. Pass api_key=... or set the IAPP_API_KEY environment variable. "
            "Get a key at https://iapp.co.th."
        )
    return key


def error_for(response: httpx.Response) -> IAppError:
    status = response.status_code
    snippet = response.text[:500]
    if status == 401:
        msg = "Authentication failed (401). Check that your iApp API key is valid."
    elif status == 402:
        msg = f"Insufficient credits (402). Top up iApp credits (IC) at https://iapp.co.th. Details: {snippet}"
    elif status == 413:
        msg = "File too large (413). Check the size limit for this service."
    elif status == 429:
        msg = "Rate limit exceeded (429). Wait a moment before retrying."
    else:
        msg = f"iApp API request failed with status {status}. Details: {snippet}"
    return IAppError(msg, status_code=status, response_text=response.text)


def build_files(file_fields: Optional[List[Tuple[str, str]]]):
    """Read (field, path) tuples into httpx multipart file payloads."""
    if not file_fields:
        return None
    payload = []
    for field, file_path in file_fields:
        path = os.path.expanduser(file_path)
        if not os.path.isfile(path):
            raise IAppError(f"Input file not found: {file_path}")
        with open(path, "rb") as f:
            payload.append((field, (os.path.basename(path), f.read())))
    return payload


def parse_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except (json.JSONDecodeError, ValueError):
        return {"raw": response.text}


def save_binary(content: bytes, output_path: str) -> str:
    path = os.path.abspath(os.path.expanduser(output_path))
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)
    return path


def save_pcm_as_wav(pcm: bytes, output_path: str, sample_rate: int = 24000) -> str:
    path = os.path.abspath(os.path.expanduser(output_path))
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(pcm)
    return path


# ── namespaces (defined once, shared by sync and async clients) ──────────────


class _Namespace:
    def __init__(self, client):
        self._c = client


class Ekyc(_Namespace):
    def thai_id_card(self, file_path: str, side: str = "front", options: Optional[str] = None):
        data = {"options": options} if options else None
        return self._c._call("POST", f"/v3/store/ekyc/thai-national-id-card/{side}", data=data, files=[("file", file_path)])

    def thai_id_card_photocopy(self, file_path: str):
        return self._c._call("POST", "/v3/store/ekyc/thai-national-id-card-with-signature", files=[("file", file_path)])

    def passport(self, file_path: str, segmentation: bool = False):
        data = {"options": "segmentation"} if segmentation else None
        return self._c._call("POST", "/v3/store/ekyc/passport", data=data, files=[("file", file_path)])

    def driver_license(self, file_path: str):
        return self._c._call("POST", "/v3/store/ekyc/thai-driver-license", files=[("file", file_path)])

    def book_bank(self, file_path: str):
        return self._c._call("POST", "/v3/store/ekyc/book-bank", files=[("file", file_path)])

    def face_verification(self, image1_path: str, image2_path: str, threshold: Optional[float] = None):
        data = {"threshold": str(threshold)} if threshold is not None else None
        return self._c._call("POST", "/v3/store/ekyc/face-verification", data=data, files=[("file1", image1_path), ("file2", image2_path)])

    def face_detection(self, file_path: str, mode: str = "single"):
        return self._c._call("POST", f"/v3/store/ekyc/face-detection/{mode}", files=[("file", file_path)])

    def face_liveness(self, file_path: str):
        return self._c._call("POST", "/v3/store/ekyc/face-passive-liveness", files=[("file", file_path)])

    def face_id_card_kyc(self, id_card_path: str, selfie_path: str):
        return self._c._call("POST", "/v3/store/ekyc/face-and-id-card-verification", files=[("file0", id_card_path), ("file1", selfie_path)])

    def face_recognition(
        self,
        action: str,
        company: str,
        file_path: Optional[str] = None,
        name: Optional[str] = None,
        password: Optional[str] = None,
        face_id: Optional[str] = None,
    ):
        if action not in _FACE_RECOGNITION_ENDPOINTS:
            raise IAppError(f"Unknown face_recognition action: {action}")
        data: Dict[str, str] = {"company": company}
        if name:
            data["name"] = name
        if password:
            data["password"] = password
        if face_id:
            data["face_id"] = face_id
        files = [("file", file_path)] if file_path else None
        return self._c._call("POST", _FACE_RECOGNITION_ENDPOINTS[action], data=data, files=files)


class Ocr(_Namespace):
    def document(self, file_path: str, mode: str = "text"):
        endpoint = {
            "text": "/v3/store/ocr/document/ocr",
            "layout": "/v3/store/ocr/document/layout",
            "docx": "/v3/store/ocr/document/docx",
        }[mode]
        return self._c._call("POST", endpoint, files=[("file", file_path)])

    def receipt(self, file_path: str, return_ocr: bool = False):
        return self._c._call("POST", "/ocr/v3/receipt/file", data={"return_ocr": str(return_ocr).lower()}, files=[("file", file_path)])

    def credit_card_statement(self, file_path: str, return_ocr: bool = False):
        return self._c._call("POST", "/ocr/v3/creditcard-statement/file", data={"return_ocr": str(return_ocr).lower()}, files=[("file", file_path)])

    def tax_deduction_certificate(self, file_path: str, return_ocr: bool = False):
        return self._c._call("POST", "/ocr/v3/tax-deduction-certificate/file", data={"return_ocr": str(return_ocr).lower()}, files=[("file", file_path)])

    def civil_registration(self, file_path: str, return_ocr: bool = False):
        return self._c._call("POST", "/ocr/v3/civil-registeration-certificate/file", data={"return_ocr": str(return_ocr).lower()}, files=[("file", file_path)])

    def resume(self, file_path: str):
        return self._c._call("POST", "/v3/store/ocr/curriculum-vitae", files=[("file", file_path)])

    def job_description(self, file_path: str):
        return self._c._call("POST", "/v3/store/ocr/job-description", files=[("file", file_path)])


class Llm(_Namespace):
    def chat(
        self,
        prompt: Optional[str] = None,
        model: str = "chinda-qwen3-4b",
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ):
        if model not in _LLM_ENDPOINTS:
            raise IAppError(f"Unknown model: {model}. Choose from {sorted(_LLM_ENDPOINTS)}")
        if not messages:
            if prompt is None:
                raise IAppError("Provide either prompt or messages.")
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
        body = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }
        return self._c._call("POST", _LLM_ENDPOINTS[model], json=body)

    def thanoy_legal_qa(self, query: str):
        return self._c._call("POST", "/v3/store/llm/thanoy-legal-ai", json={"query": query})


class Nlp(_Namespace):
    def translate(self, text: str, source_lang: str, target_lang: str, max_length: Optional[int] = None):
        data = {"text": text, "source_lang": source_lang, "target_lang": target_lang}
        if max_length is not None:
            data["max_length"] = str(max_length)
        return self._c._call("POST", "/v1/text/translate", data=data)

    def summarize(self, text: str, style: str = "standard", language: str = "th", max_output_tokens: Optional[int] = None):
        body: Dict[str, Any] = {"text": text, "style": style, "language": language}
        if max_output_tokens is not None:
            body["max_output_tokens"] = max_output_tokens
        return self._c._call("POST", "/v3/store/nlp/thai-text-summary", json=body)

    def sentiment(self, text: str):
        return self._c._call("POST", "/v3/store/nlp/sentiment-analysis", params={"text": text})

    def toxicity(self, text: str):
        return self._c._call("POST", "/v3/store/nlp/toxicity-classification", params={"text": text})

    def qa(self, question: str, document: str):
        return self._c._call("POST", "/thai-qa", json={"question": question, "document": document})

    def question_generation(self, text: str):
        return self._c._call("GET", "/v3/store/nlp/question/generation", params={"text": text})


class Speech(_Namespace):
    def transcribe(self, file_path: str, language: str = "th", quality: str = "base", chunk_size: Optional[int] = None):
        key = (language, quality)
        if key not in _STT_ENDPOINTS:
            raise IAppError(f"Unsupported language/quality: {key}")
        data: Dict[str, str] = {}
        if chunk_size is not None:
            data["chunk_size"] = str(chunk_size)
        if quality == "pro":
            data["use_asr_pro"] = "1"
        return self._c._call("POST", _STT_ENDPOINTS[key], data=data or None, files=[("file", file_path)])

    def tts(self, text: str, output_path: str, voice: str = "kaitom-v3", speed: float = 1.0):
        if voice == "kaitom-v3":
            return self._c._call(
                "POST", "/v3/store/audio/tts", json={"text": text, "speed": speed},
                transform=lambda r: save_pcm_as_wav(r.content, output_path),
            )
        if voice == "kaitom-v2":
            return self._c._call(
                "POST", "/v3/store/speech/text-to-speech/kaitom", data={"text": text, "language": "TH_MIX_EN"},
                transform=lambda r: save_binary(r.content, output_path),
            )
        if voice == "kaitom-v1":
            return self._c._call(
                "GET", "/v3/store/speech/text-to-speech/kaitom/v1", params={"text": text},
                transform=lambda r: save_binary(r.content, output_path),
            )
        if voice == "cee":
            return self._c._call(
                "GET", "/v3/store/speech/text-to-speech/cee", params={"text": text},
                transform=lambda r: save_binary(r.content, output_path),
            )
        raise IAppError(f"Unknown voice: {voice}")

    def voice_clone(self, text: str, ref_audio_path: str, ref_text: str, output_path: str):
        return self._c._call(
            "POST", "/v3/store/audio/tts/clone",
            data={"text": text, "ref_text": ref_text},
            files=[("ref_audio", ref_audio_path)],
            transform=lambda r: save_binary(r.content, output_path),
        )

    def ai_audio_detection(self, audio_path: str):
        return self._c._call("POST", "/v3/store/audio/tts/detect", files=[("audio", audio_path)])


class Image(_Namespace):
    def generate(self, prompt: str, output_path: str, model: str = "nanobanana"):
        endpoint = (
            "/v3/image/generation/google/nanobanana/generate"
            if model == "nanobanana"
            else "/v3/image/generation/google/nanobananapro/generate"
        )

        def transform(response: httpx.Response):
            payload = response.json()
            saved, notes = None, []
            for candidate in payload.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    inline = part.get("inlineData")
                    if inline and inline.get("data") and saved is None:
                        saved = save_binary(base64.b64decode(inline["data"]), output_path)
                    elif part.get("text"):
                        notes.append(part["text"])
            if saved is None:
                raise IAppError(f"No image data in response: {str(payload)[:300]}")
            return {"path": saved, "notes": "\n".join(notes)}

        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        }
        return self._c._call("POST", endpoint, json=body, transform=transform)

    def remove_background(self, file_path: str, output_path: str):
        return self._c._call(
            "POST", "/v3/store/smart-city/remove-background", files=[("file", file_path)],
            transform=lambda r: save_binary(r.content, output_path),
        )


class Video(_Namespace):
    def submit(
        self,
        prompt: str,
        model: str = "seedance-fast",
        duration: int = 5,
        ratio: str = "16:9",
        resolution: str = "720p",
        generate_audio: bool = True,
        watermark: bool = False,
        first_frame_image_url: Optional[str] = None,
        reference_image_url: Optional[str] = None,
    ):
        content: List[Dict[str, Any]] = [{"type": "text", "text": prompt}]
        if first_frame_image_url:
            content.append({"type": "image_url", "image_url": {"url": first_frame_image_url}, "role": "first_frame"})
        if reference_image_url:
            content.append({"type": "image_url", "image_url": {"url": reference_image_url}, "role": "reference_image"})
        body = {
            "model": _VIDEO_MODELS[model],
            "content": content,
            "duration": duration,
            "ratio": ratio,
            "resolution": resolution,
            "generate_audio": generate_audio,
            "watermark": watermark,
        }
        return self._c._call("POST", "/v3/store/video/seedance/tasks", json=body)

    def status(self, task_id: str):
        return self._c._call("GET", f"/v3/store/video/seedance/tasks/{task_id}")


class SmartCity(_Namespace):
    def license_plate(self, file_path: str):
        return self._c._call("POST", "/v3/store/smart-city/license-plate-ocr", files=[("file", file_path)])

    def meter(self, file_path: str):
        return self._c._call("POST", "/v3/store/smart-city/power-meter-and-water-meter/file", files=[("file", file_path)])

    def route_optimization(
        self,
        origin_address: str,
        origin_latitude: float,
        origin_longitude: float,
        stops: List[Dict[str, Any]],
        driver_count: int = -1,
    ):
        body = {
            "driverSize": driver_count,
            "origin": {
                "address": origin_address,
                "latitude": origin_latitude,
                "longitude": origin_longitude,
            },
            "routes": stops,
        }
        return self._c._call("POST", "/v3/store/smart-city/automatic-route-optimization", json=body)


class Data(_Namespace):
    def thai_holidays(
        self,
        year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_before: int = 0,
        days_after: int = 365,
        holiday_type: str = "public",
    ):
        params: Dict[str, Any] = {"holiday_type": holiday_type}
        if year is not None:
            return self._c._call("GET", f"/v3/store/data/thai-holiday/year/{year}", params=params)
        if start_date and end_date:
            params.update({"start_date": start_date, "end_date": end_date})
            return self._c._call("GET", "/v3/store/data/thai-holiday/range", params=params)
        params.update({"days_before": days_before, "days_after": days_after})
        return self._c._call("GET", "/v3/store/data/thai-holiday", params=params)


def attach_namespaces(client) -> None:
    client.ekyc = Ekyc(client)
    client.ocr = Ocr(client)
    client.llm = Llm(client)
    client.nlp = Nlp(client)
    client.speech = Speech(client)
    client.image = Image(client)
    client.video = Video(client)
    client.smartcity = SmartCity(client)
    client.data = Data(client)
