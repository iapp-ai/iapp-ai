/** Tests for the modern Node SDK — fetch is mocked, no network calls. */
"use strict";

const { test, beforeEach, afterEach } = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const iapp_ai = require("../src/index.js");
const { IAppClient, IAppError } = iapp_ai;

// ── fetch mock ───────────────────────────────────────────────────────────────

const realFetch = globalThis.fetch;
let calls = [];
let nextResponse = () => new Response(JSON.stringify({ ok: true }), { status: 200 });

beforeEach(() => {
  calls = [];
  nextResponse = () => new Response(JSON.stringify({ ok: true }), { status: 200 });
  globalThis.fetch = async (url, init) => {
    calls.push({ url: new URL(url), init });
    return nextResponse();
  };
});

afterEach(() => {
  globalThis.fetch = realFetch;
});

function tmpFile(name, content = "fake") {
  const p = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "iapp-")), name);
  fs.writeFileSync(p, content);
  return p;
}

// ── legacy compatibility ─────────────────────────────────────────────────────

test("default export is still the legacy v1.x class", () => {
  const legacy = new iapp_ai("k");
  assert.strictEqual(legacy.apikey, "k");
  assert.strictEqual(typeof legacy.idcardFront_Ocr, "function");
  assert.strictEqual(typeof legacy.thai_qa, "function");
});

// ── modern client basics ─────────────────────────────────────────────────────

test("requires an API key", () => {
  const saved = process.env.IAPP_API_KEY;
  delete process.env.IAPP_API_KEY;
  assert.throws(() => new IAppClient(), IAppError);
  if (saved !== undefined) process.env.IAPP_API_KEY = saved;
});

test("reads key from env", () => {
  process.env.IAPP_API_KEY = "env-key";
  assert.strictEqual(new IAppClient().apiKey, "env-key");
  delete process.env.IAPP_API_KEY;
});

test("sends apikey header", async () => {
  const c = new IAppClient("k");
  await c.nlp.sentiment("hello");
  assert.strictEqual(calls[0].init.headers.apikey, "k");
});

test("maps 401 to IAppError with statusCode", async () => {
  nextResponse = () => new Response("denied", { status: 401 });
  const c = new IAppClient("k");
  await assert.rejects(
    () => c.nlp.sentiment("x"),
    (err) => err instanceof IAppError && err.statusCode === 401
  );
});

// ── endpoint mapping (the live-verified paths) ───────────────────────────────

test("nlp endpoints", async () => {
  const c = new IAppClient("k");
  await c.nlp.sentiment("t");
  await c.nlp.summarize("t");
  await c.nlp.qa("q", "d");
  await c.nlp.questionGeneration("t");
  assert.strictEqual(calls[0].url.pathname, "/v3/store/nlp/sentiment-analysis");
  assert.strictEqual(calls[1].url.pathname, "/v3/store/nlp/thai-text-summary"); // not /v2
  assert.strictEqual(calls[2].url.pathname, "/thai-qa");
  assert.strictEqual(calls[3].url.pathname, "/v3/store/nlp/question/generation");
  assert.strictEqual(calls[3].init.method, "GET"); // POST returns 405
  assert.strictEqual(calls[3].url.searchParams.get("text"), "t");
});

test("ekyc endpoints", async () => {
  const img = tmpFile("img.jpg");
  const c = new IAppClient("k");
  await c.ekyc.thaiIdCard(img);
  await c.ekyc.passport(img);
  await c.ekyc.faceRecognition("check", "co", { password: "p" });
  assert.strictEqual(calls[0].url.pathname, "/v3/store/ekyc/thai-national-id-card/front");
  assert.strictEqual(calls[1].url.pathname, "/v3/store/ekyc/passport"); // not /v2
  assert.strictEqual(calls[2].url.pathname, "/v3/store/ekyc/face-recognition/check");
});

test("llm chat is non-streaming and maps models", async () => {
  nextResponse = () => new Response(JSON.stringify({ choices: [] }), { status: 200 });
  const c = new IAppClient("k");
  await c.llm.chat("hi", { model: "deepseek-v4-pro" });
  assert.strictEqual(calls[0].url.pathname, "/v3/llm/deepseek-v4/chat/completions");
  const body = JSON.parse(calls[0].init.body);
  assert.strictEqual(body.stream, false);
  assert.deepStrictEqual(body.messages.at(-1), { role: "user", content: "hi" });
});

test("speech tts kaitom-v3 wraps PCM into a WAV file", async () => {
  nextResponse = () => new Response(Buffer.alloc(200), { status: 200 });
  const out = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "iapp-")), "out.wav");
  const c = new IAppClient("k");
  const saved = await c.speech.tts("สวัสดี", out);
  assert.strictEqual(calls[0].url.pathname, "/v3/store/audio/tts");
  assert.strictEqual(fs.readFileSync(saved).subarray(0, 4).toString(), "RIFF");
});

test("speech transcribe pro sends use_asr_pro flag", async () => {
  const wav = tmpFile("a.wav");
  const c = new IAppClient("k");
  await c.speech.transcribe(wav, { quality: "pro" });
  assert.strictEqual(calls[0].url.pathname, "/v3/store/speech/speech-to-text/pro");
  assert.strictEqual(calls[0].init.body.get("use_asr_pro"), "1");
});

test("image generate decodes base64 and saves the file", async () => {
  const data = Buffer.from("fake-png").toString("base64");
  nextResponse = () =>
    new Response(JSON.stringify({ candidates: [{ content: { parts: [{ inlineData: { data } }] } }] }), { status: 200 });
  const out = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "iapp-")), "out.png");
  const c = new IAppClient("k");
  const result = await c.image.generate("p", out);
  assert.strictEqual(calls[0].url.pathname, "/v3/image/generation/google/nanobanana/generate");
  assert.strictEqual(fs.readFileSync(result.path).toString(), "fake-png");
});

test("video submit maps model names", async () => {
  const c = new IAppClient("k");
  await c.video.submit("p", { model: "seedance-fast" });
  await c.video.status("t1");
  assert.strictEqual(calls[0].url.pathname, "/v3/store/video/seedance/tasks");
  assert.strictEqual(JSON.parse(calls[0].init.body).model, "dreamina-seedance-2-0-fast-260128");
  assert.strictEqual(calls[1].url.pathname, "/v3/store/video/seedance/tasks/t1");
});

test("data thaiHolidays three modes", async () => {
  const c = new IAppClient("k");
  await c.data.thaiHolidays({ year: 2026 });
  await c.data.thaiHolidays({ startDate: "2026-01-01", endDate: "2026-12-31" });
  await c.data.thaiHolidays();
  assert.strictEqual(calls[0].url.pathname, "/v3/store/data/thai-holiday/year/2026");
  assert.strictEqual(calls[1].url.pathname, "/v3/store/data/thai-holiday/range");
  assert.strictEqual(calls[2].url.pathname, "/v3/store/data/thai-holiday");
});

test("all namespaces and methods exist", () => {
  const c = new IAppClient("k");
  const expected = {
    ekyc: ["thaiIdCard", "thaiIdCardPhotocopy", "passport", "driverLicense", "bookBank", "faceVerification", "faceDetection", "faceLiveness", "faceIdCardKyc", "faceRecognition"],
    ocr: ["document", "receipt", "creditCardStatement", "taxDeductionCertificate", "civilRegistration", "resume", "jobDescription"],
    llm: ["chat", "thanoyLegalQa"],
    nlp: ["translate", "summarize", "sentiment", "toxicity", "qa", "questionGeneration"],
    speech: ["transcribe", "tts", "voiceClone", "aiAudioDetection"],
    image: ["generate", "removeBackground"],
    video: ["submit", "status"],
    smartcity: ["licensePlate", "meter", "routeOptimization"],
    data: ["thaiHolidays"],
  };
  for (const [ns, methods] of Object.entries(expected)) {
    for (const m of methods) {
      assert.strictEqual(typeof c[ns][m], "function", `missing ${ns}.${m}`);
    }
  }
});
