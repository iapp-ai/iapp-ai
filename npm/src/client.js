/**
 * Modern iApp AI SDK for Node.js (fetch-based, Node 18+).
 *
 * const { IAppClient } = require("iapp_ai");
 * const client = new IAppClient("YOUR_API_KEY");       // or IAPP_API_KEY env var
 * const result = await client.nlp.sentiment("ร้านนี้อร่อยมาก");
 *
 * All endpoints were verified end-to-end against the live API (2026-06).
 */
"use strict";

const fs = require("node:fs");
const path = require("node:path");

const API_BASE = "https://api.iapp.co.th";

const STT_ENDPOINTS = {
  "th:base": "/v3/store/speech/speech-to-text/base",
  "th:pro": "/v3/store/speech/speech-to-text/pro",
  "en:base": "/v3/store/speech/speech-to-text/base/en",
  "en:pro": "/v3/store/speech/speech-to-text/pro/en",
  "zh:base": "/v3/store/speech/speech-to-text/base/zh",
  "zh:pro": "/v3/store/speech/speech-to-text/pro/zh",
};

const LLM_ENDPOINTS = {
  "chinda-qwen3-4b": "/v3/llm/chinda-thaillm-4b/chat/completions",
  "deepseek-reasoner": "/v3/llm/deepseek-3p2/chat/completions",
  "deepseek-chat": "/v3/llm/deepseek-3p2/chat/completions",
  "deepseek-v4-flash": "/v3/llm/deepseek-v4/chat/completions",
  "deepseek-v4-pro": "/v3/llm/deepseek-v4/chat/completions",
};

const VIDEO_MODELS = {
  seedance: "dreamina-seedance-2-0-260128",
  "seedance-fast": "dreamina-seedance-2-0-fast-260128",
};

const FACE_RECOGNITION_ENDPOINTS = {
  recognize_single: "/v3/store/ekyc/face-recognition/single",
  recognize_multi: "/v3/store/ekyc/face-recognition/multi",
  add: "/v3/store/ekyc/face-recognition/add",
  remove: "/v3/store/ekyc/face-recognition/remove",
  check: "/v3/store/ekyc/face-recognition/check",
};

class IAppError extends Error {
  constructor(message, statusCode = null, responseText = "") {
    super(message);
    this.name = "IAppError";
    this.statusCode = statusCode;
    this.responseText = responseText;
  }
}

function errorMessage(status, snippet) {
  if (status === 401) return "Authentication failed (401). Check that your iApp API key is valid.";
  if (status === 402) return `Insufficient credits (402). Top up iApp credits (IC) at https://iapp.co.th. Details: ${snippet}`;
  if (status === 413) return "File too large (413). Check the size limit for this service.";
  if (status === 429) return "Rate limit exceeded (429). Wait a moment before retrying.";
  return `iApp API request failed with status ${status}. Details: ${snippet}`;
}

function fileBlob(filePath) {
  if (!fs.existsSync(filePath)) throw new IAppError(`Input file not found: ${filePath}`);
  return new Blob([fs.readFileSync(filePath)]);
}

function saveBinary(buffer, outputPath) {
  const resolved = path.resolve(outputPath);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  fs.writeFileSync(resolved, Buffer.from(buffer));
  return resolved;
}

/** Wrap raw signed 16-bit mono PCM in a WAV container. */
function pcmToWav(pcm, sampleRate = 24000) {
  const data = Buffer.from(pcm);
  const header = Buffer.alloc(44);
  header.write("RIFF", 0);
  header.writeUInt32LE(36 + data.length, 4);
  header.write("WAVE", 8);
  header.write("fmt ", 12);
  header.writeUInt32LE(16, 16); // PCM chunk size
  header.writeUInt16LE(1, 20); // PCM format
  header.writeUInt16LE(1, 22); // mono
  header.writeUInt32LE(sampleRate, 24);
  header.writeUInt32LE(sampleRate * 2, 28); // byte rate
  header.writeUInt16LE(2, 32); // block align
  header.writeUInt16LE(16, 34); // bits per sample
  header.write("data", 36);
  header.writeUInt32LE(data.length, 40);
  return Buffer.concat([header, data]);
}

class IAppClient {
  constructor(apiKey, { baseUrl = API_BASE } = {}) {
    this.apiKey = (apiKey || process.env.IAPP_API_KEY || "").trim();
    if (!this.apiKey) {
      throw new IAppError(
        "No API key. Pass new IAppClient(apiKey) or set the IAPP_API_KEY environment variable. " +
          "Get a key at https://iapp.co.th."
      );
    }
    this.baseUrl = baseUrl;

    const c = this;

    this.ekyc = {
      thaiIdCard: (filePath, { side = "front", options = null } = {}) =>
        c._call("POST", `/v3/store/ekyc/thai-national-id-card/${side}`, { form: options ? { options } : null, files: { file: filePath } }),
      thaiIdCardPhotocopy: (filePath) =>
        c._call("POST", "/v3/store/ekyc/thai-national-id-card-with-signature", { files: { file: filePath } }),
      passport: (filePath, { segmentation = false } = {}) =>
        c._call("POST", "/v3/store/ekyc/passport", { form: segmentation ? { options: "segmentation" } : null, files: { file: filePath } }),
      driverLicense: (filePath) =>
        c._call("POST", "/v3/store/ekyc/thai-driver-license", { files: { file: filePath } }),
      bookBank: (filePath) =>
        c._call("POST", "/v3/store/ekyc/book-bank", { files: { file: filePath } }),
      faceVerification: (image1Path, image2Path, { threshold = null } = {}) =>
        c._call("POST", "/v3/store/ekyc/face-verification", { form: threshold != null ? { threshold: String(threshold) } : null, files: { file1: image1Path, file2: image2Path } }),
      faceDetection: (filePath, { mode = "single" } = {}) =>
        c._call("POST", `/v3/store/ekyc/face-detection/${mode}`, { files: { file: filePath } }),
      faceLiveness: (filePath) =>
        c._call("POST", "/v3/store/ekyc/face-passive-liveness", { files: { file: filePath } }),
      faceIdCardKyc: (idCardPath, selfiePath) =>
        c._call("POST", "/v3/store/ekyc/face-and-id-card-verification", { files: { file0: idCardPath, file1: selfiePath } }),
      faceRecognition: (action, company, { filePath = null, name = null, password = null, faceId = null } = {}) => {
        const endpoint = FACE_RECOGNITION_ENDPOINTS[action];
        if (!endpoint) throw new IAppError(`Unknown face recognition action: ${action}`);
        const form = { company };
        if (name) form.name = name;
        if (password) form.password = password;
        if (faceId) form.face_id = faceId;
        return c._call("POST", endpoint, { form, files: filePath ? { file: filePath } : null });
      },
    };

    this.ocr = {
      document: (filePath, { mode = "text" } = {}) => {
        const endpoint = { text: "/v3/store/ocr/document/ocr", layout: "/v3/store/ocr/document/layout", docx: "/v3/store/ocr/document/docx" }[mode];
        if (!endpoint) throw new IAppError(`Unknown document OCR mode: ${mode}`);
        return c._call("POST", endpoint, { files: { file: filePath } });
      },
      receipt: (filePath, { returnOcr = false } = {}) =>
        c._call("POST", "/ocr/v3/receipt/file", { form: { return_ocr: String(returnOcr) }, files: { file: filePath } }),
      creditCardStatement: (filePath, { returnOcr = false } = {}) =>
        c._call("POST", "/ocr/v3/creditcard-statement/file", { form: { return_ocr: String(returnOcr) }, files: { file: filePath } }),
      taxDeductionCertificate: (filePath, { returnOcr = false } = {}) =>
        c._call("POST", "/ocr/v3/tax-deduction-certificate/file", { form: { return_ocr: String(returnOcr) }, files: { file: filePath } }),
      civilRegistration: (filePath, { returnOcr = false } = {}) =>
        c._call("POST", "/ocr/v3/civil-registeration-certificate/file", { form: { return_ocr: String(returnOcr) }, files: { file: filePath } }),
      resume: (filePath) =>
        c._call("POST", "/v3/store/ocr/curriculum-vitae", { files: { file: filePath } }),
      jobDescription: (filePath) =>
        c._call("POST", "/v3/store/ocr/job-description", { files: { file: filePath } }),
    };

    this.llm = {
      chat: (prompt, { model = "chinda-qwen3-4b", systemPrompt = null, messages = null, maxTokens = 4096, temperature = 0.7 } = {}) => {
        const endpoint = LLM_ENDPOINTS[model];
        if (!endpoint) throw new IAppError(`Unknown model: ${model}`);
        let msgs = messages;
        if (!msgs) {
          msgs = [];
          if (systemPrompt) msgs.push({ role: "system", content: systemPrompt });
          msgs.push({ role: "user", content: prompt });
        }
        return c._call("POST", endpoint, {
          json: { model, messages: msgs, max_tokens: maxTokens, temperature, stream: false },
        });
      },
      thanoyLegalQa: (query) =>
        c._call("POST", "/v3/store/llm/thanoy-legal-ai", { json: { query } }),
    };

    this.nlp = {
      translate: (text, sourceLang, targetLang, { maxLength = null } = {}) => {
        const form = { text, source_lang: sourceLang, target_lang: targetLang };
        if (maxLength != null) form.max_length = String(maxLength);
        return c._call("POST", "/v1/text/translate", { urlencoded: form });
      },
      summarize: (text, { style = "standard", language = "th", maxOutputTokens = null } = {}) => {
        const json = { text, style, language };
        if (maxOutputTokens != null) json.max_output_tokens = maxOutputTokens;
        return c._call("POST", "/v3/store/nlp/thai-text-summary", { json });
      },
      sentiment: (text) =>
        c._call("POST", "/v3/store/nlp/sentiment-analysis", { params: { text } }),
      toxicity: (text) =>
        c._call("POST", "/v3/store/nlp/toxicity-classification", { params: { text } }),
      qa: (question, document) =>
        c._call("POST", "/thai-qa", { json: { question, document } }),
      questionGeneration: (text) =>
        c._call("GET", "/v3/store/nlp/question/generation", { params: { text } }),
    };

    this.speech = {
      transcribe: (filePath, { language = "th", quality = "base", chunkSize = null } = {}) => {
        const endpoint = STT_ENDPOINTS[`${language}:${quality}`];
        if (!endpoint) throw new IAppError(`Unsupported language/quality: ${language}/${quality}`);
        const form = {};
        if (chunkSize != null) form.chunk_size = String(chunkSize);
        if (quality === "pro") form.use_asr_pro = "1";
        return c._call("POST", endpoint, { form, files: { file: filePath } });
      },
      tts: (text, outputPath, { voice = "kaitom-v3", speed = 1.0 } = {}) => {
        if (voice === "kaitom-v3") {
          return c._call("POST", "/v3/store/audio/tts", { json: { text, speed }, binary: true })
            .then((buf) => saveBinary(pcmToWav(buf), outputPath));
        }
        if (voice === "kaitom-v2") {
          return c._call("POST", "/v3/store/speech/text-to-speech/kaitom", { urlencoded: { text, language: "TH_MIX_EN" }, binary: true })
            .then((buf) => saveBinary(buf, outputPath));
        }
        if (voice === "kaitom-v1") {
          return c._call("GET", "/v3/store/speech/text-to-speech/kaitom/v1", { params: { text }, binary: true })
            .then((buf) => saveBinary(buf, outputPath));
        }
        if (voice === "cee") {
          return c._call("GET", "/v3/store/speech/text-to-speech/cee", { params: { text }, binary: true })
            .then((buf) => saveBinary(buf, outputPath));
        }
        throw new IAppError(`Unknown voice: ${voice}`);
      },
      voiceClone: (text, refAudioPath, refText, outputPath) =>
        c._call("POST", "/v3/store/audio/tts/clone", { form: { text, ref_text: refText }, files: { ref_audio: refAudioPath }, binary: true })
          .then((buf) => saveBinary(buf, outputPath)),
      aiAudioDetection: (audioPath) =>
        c._call("POST", "/v3/store/audio/tts/detect", { files: { audio: audioPath } }),
    };

    this.image = {
      generate: async (prompt, outputPath, { model = "nanobanana" } = {}) => {
        const endpoint =
          model === "nanobanana"
            ? "/v3/image/generation/google/nanobanana/generate"
            : "/v3/image/generation/google/nanobananapro/generate";
        const payload = await c._call("POST", endpoint, {
          json: { contents: [{ parts: [{ text: prompt }] }], generationConfig: { responseModalities: ["TEXT", "IMAGE"] } },
        });
        let saved = null;
        const notes = [];
        for (const candidate of payload.candidates || []) {
          for (const part of candidate.content?.parts || []) {
            if (part.inlineData?.data && !saved) {
              saved = saveBinary(Buffer.from(part.inlineData.data, "base64"), outputPath);
            } else if (part.text) {
              notes.push(part.text);
            }
          }
        }
        if (!saved) throw new IAppError(`No image data in response: ${JSON.stringify(payload).slice(0, 300)}`);
        return { path: saved, notes: notes.join("\n") };
      },
      removeBackground: (filePath, outputPath) =>
        c._call("POST", "/v3/store/smart-city/remove-background", { files: { file: filePath }, binary: true })
          .then((buf) => saveBinary(buf, outputPath)),
    };

    this.video = {
      submit: (prompt, { model = "seedance-fast", duration = 5, ratio = "16:9", resolution = "720p", generateAudio = true, watermark = false, firstFrameImageUrl = null, referenceImageUrl = null } = {}) => {
        const content = [{ type: "text", text: prompt }];
        if (firstFrameImageUrl) content.push({ type: "image_url", image_url: { url: firstFrameImageUrl }, role: "first_frame" });
        if (referenceImageUrl) content.push({ type: "image_url", image_url: { url: referenceImageUrl }, role: "reference_image" });
        return c._call("POST", "/v3/store/video/seedance/tasks", {
          json: { model: VIDEO_MODELS[model], content, duration, ratio, resolution, generate_audio: generateAudio, watermark },
        });
      },
      status: (taskId) => c._call("GET", `/v3/store/video/seedance/tasks/${taskId}`),
    };

    this.smartcity = {
      licensePlate: (filePath) =>
        c._call("POST", "/v3/store/smart-city/license-plate-ocr", { files: { file: filePath } }),
      meter: (filePath) =>
        c._call("POST", "/v3/store/smart-city/power-meter-and-water-meter/file", { files: { file: filePath } }),
      routeOptimization: ({ originAddress, originLatitude, originLongitude, stops, driverCount = -1 }) =>
        c._call("POST", "/v3/store/smart-city/automatic-route-optimization", {
          json: { driverSize: driverCount, origin: { address: originAddress, latitude: originLatitude, longitude: originLongitude }, routes: stops },
        }),
    };

    this.data = {
      thaiHolidays: ({ year = null, startDate = null, endDate = null, daysBefore = 0, daysAfter = 365, holidayType = "public" } = {}) => {
        const params = { holiday_type: holidayType };
        if (year != null) return c._call("GET", `/v3/store/data/thai-holiday/year/${year}`, { params });
        if (startDate && endDate) {
          return c._call("GET", "/v3/store/data/thai-holiday/range", { params: { ...params, start_date: startDate, end_date: endDate } });
        }
        return c._call("GET", "/v3/store/data/thai-holiday", { params: { ...params, days_before: String(daysBefore), days_after: String(daysAfter) } });
      },
    };
  }

  async _call(method, apiPath, { params = null, form = null, urlencoded = null, json = null, files = null, binary = false } = {}) {
    const url = new URL(this.baseUrl + apiPath);
    for (const [k, v] of Object.entries(params || {})) url.searchParams.set(k, v);

    const headers = { apikey: this.apiKey };
    let body;
    if (files) {
      const fd = new FormData();
      for (const [k, v] of Object.entries(form || {})) fd.append(k, v);
      for (const [field, filePath] of Object.entries(files)) {
        fd.append(field, fileBlob(filePath), path.basename(filePath));
      }
      body = fd; // fetch sets the multipart content-type + boundary
    } else if (json) {
      headers["content-type"] = "application/json";
      body = JSON.stringify(json);
    } else if (urlencoded || form) {
      body = new URLSearchParams(urlencoded || form);
    }

    let response;
    try {
      response = await fetch(url, { method, headers, body });
    } catch (err) {
      throw new IAppError(`Network error calling the iApp API: ${err.message}`);
    }
    if (!response.ok) {
      const text = await response.text();
      throw new IAppError(errorMessage(response.status, text.slice(0, 500)), response.status, text);
    }
    if (binary) return Buffer.from(await response.arrayBuffer());
    const text = await response.text();
    try {
      return JSON.parse(text);
    } catch {
      return { raw: text };
    }
  }
}

module.exports = { IAppClient, IAppError, API_BASE };
