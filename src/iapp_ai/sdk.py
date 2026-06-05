"""Modern iApp AI SDK clients (sync and async).

Usage::

    from iapp_ai import IAppClient

    client = IAppClient(api_key="...")          # or set IAPP_API_KEY env var
    result = client.nlp.sentiment("ร้านนี้อร่อยมาก")
    text = client.ocr.document("contract.pdf")
    client.speech.tts("สวัสดี", output_path="hello.wav")

Async::

    from iapp_ai import AsyncIAppClient

    client = AsyncIAppClient()
    result = await client.nlp.sentiment("ร้านนี้อร่อยมาก")
"""

from typing import Optional

import httpx

from iapp_ai._core import (
    API_BASE,
    TIMEOUT,
    attach_namespaces,
    build_files,
    error_for,
    parse_json,
    resolve_api_key,
)


class IAppClient:
    """Synchronous client for the iApp AI Marketplace APIs."""

    def __init__(self, api_key: Optional[str] = None, *, base_url: str = API_BASE, timeout=TIMEOUT):
        self.api_key = resolve_api_key(api_key)
        self.base_url = base_url
        self.timeout = timeout
        attach_namespaces(self)

    def _call(self, method, path, *, params=None, data=None, json=None, files=None, transform=None):
        file_payload = build_files(files)
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            response = client.request(
                method, path, headers={"apikey": self.api_key},
                params=params, data=data, json=json, files=file_payload,
            )
        if response.status_code >= 400:
            raise error_for(response)
        return transform(response) if transform else parse_json(response)


class AsyncIAppClient:
    """Asynchronous client for the iApp AI Marketplace APIs."""

    def __init__(self, api_key: Optional[str] = None, *, base_url: str = API_BASE, timeout=TIMEOUT):
        self.api_key = resolve_api_key(api_key)
        self.base_url = base_url
        self.timeout = timeout
        attach_namespaces(self)

    async def _call(self, method, path, *, params=None, data=None, json=None, files=None, transform=None):
        file_payload = build_files(files)
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.request(
                method, path, headers={"apikey": self.api_key},
                params=params, data=data, json=json, files=file_payload,
            )
        if response.status_code >= 400:
            raise error_for(response)
        return transform(response) if transform else parse_json(response)
