"""iApp AI — Python SDK + MCP server for the iApp AI Marketplace.

Since v2.0.0 this package ships three things:

1. The modern SDK (sync and async), covering all live-verified endpoints::

       from iapp_ai import IAppClient
       client = IAppClient(api_key="YOUR_API_KEY")   # or IAPP_API_KEY env var
       result = client.nlp.sentiment("ร้านนี้อร่อยมาก")

2. The legacy SDK class, unchanged from v1.4.0 for backward compatibility::

       from iapp_ai import api
       client = api("YOUR_API_KEY")

3. The iApp AI MCP server (``iapp-ai`` console command / ``iapp_mcp`` package),
   which exposes 37 tools over the Model Context Protocol. See
   https://github.com/iapp-ai/iapp-ai for documentation.
"""

__author__ = """Kobkrit Viriyayudhakorn"""
__email__ = "kobkrit@iapp.co.th"
__version__ = "2.0.0"

from iapp_ai.module_api import api  # noqa: F401,E402 — legacy v1.x API
from iapp_ai._core import IAppError  # noqa: F401,E402
from iapp_ai.sdk import AsyncIAppClient, IAppClient  # noqa: F401,E402
