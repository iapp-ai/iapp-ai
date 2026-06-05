# iApp AI — Node.js SDK + MCP Server

[iApp AI Marketplace](https://iapp.co.th) — Thai-focused AI APIs: OCR, eKYC,
Thai NLP, LLMs, speech, and image/video generation.

Since v2.0.0 this package ships three things:

1. **A modern SDK** (fetch-based, TypeScript types, 37 live-verified operations)
2. **The legacy Node.js SDK** (unchanged from v1.x — existing code keeps working)
3. **An MCP server launcher** (`iapp-ai` command) that connects AI assistants to 37 iApp tools

## MCP server

Add to your MCP client's configuration file
(requires [uv](https://docs.astral.sh/uv/getting-started/installation/) — the
server itself runs on Python and is fetched automatically):

```json
{
  "mcpServers": {
    "iapp-ai": {
      "command": "npx",
      "args": ["-y", "iapp_ai"],
      "env": {
        "IAPP_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

Full MCP documentation (37 tools): https://github.com/iapp-ai/iapp-ai

## SDK

```javascript
const { IAppClient } = require("iapp_ai");

const client = new IAppClient("YOUR_API_KEY");     // or IAPP_API_KEY env var

const result = await client.nlp.sentiment("ร้านนี้อร่อยมาก");
const card = await client.ekyc.thaiIdCard("idcard.jpg");
const text = await client.ocr.document("contract.pdf");
await client.speech.tts("สวัสดีครับ", "hello.wav");
const reply = await client.llm.chat("ส้มตำกี่แคลอรี่");
```

Namespaces: `ekyc`, `ocr`, `llm`, `nlp`, `speech`, `image`, `video`,
`smartcity`, `data` — TypeScript definitions included.

## Legacy SDK (v1.x compatible)

```javascript
const iapp_ai = require("iapp_ai");

const client = new iapp_ai("YOUR_API_KEY");
const result = await client.idcardFront_Ocr("idcard.jpg");
```

All v1.x methods are preserved as-is.

## Get an API key

[iapp.co.th](https://iapp.co.th) → **API Keys** → **Create New API Key**

## Support

- Documentation: [iapp.co.th/docs/intro](https://iapp.co.th/docs/intro)
- Email: support@iapp.co.th
