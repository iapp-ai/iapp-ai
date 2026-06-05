/** Type definitions for the iapp_ai package (v2). */

declare class IAppError extends Error {
  statusCode: number | null;
  responseText: string;
}

type Json = Record<string, any>;

declare class IAppClient {
  constructor(apiKey?: string, options?: { baseUrl?: string });
  apiKey: string;
  baseUrl: string;

  ekyc: {
    thaiIdCard(filePath: string, options?: { side?: "front" | "back"; options?: string }): Promise<Json>;
    thaiIdCardPhotocopy(filePath: string): Promise<Json>;
    passport(filePath: string, options?: { segmentation?: boolean }): Promise<Json>;
    driverLicense(filePath: string): Promise<Json>;
    bookBank(filePath: string): Promise<Json>;
    faceVerification(image1Path: string, image2Path: string, options?: { threshold?: number }): Promise<Json>;
    faceDetection(filePath: string, options?: { mode?: "single" | "multi" }): Promise<Json>;
    faceLiveness(filePath: string): Promise<Json>;
    faceIdCardKyc(idCardPath: string, selfiePath: string): Promise<Json>;
    faceRecognition(
      action: "recognize_single" | "recognize_multi" | "add" | "remove" | "check",
      company: string,
      options?: { filePath?: string; name?: string; password?: string; faceId?: string }
    ): Promise<Json>;
  };

  ocr: {
    document(filePath: string, options?: { mode?: "text" | "layout" | "docx" }): Promise<Json>;
    receipt(filePath: string, options?: { returnOcr?: boolean }): Promise<Json>;
    creditCardStatement(filePath: string, options?: { returnOcr?: boolean }): Promise<Json>;
    taxDeductionCertificate(filePath: string, options?: { returnOcr?: boolean }): Promise<Json>;
    civilRegistration(filePath: string, options?: { returnOcr?: boolean }): Promise<Json>;
    resume(filePath: string): Promise<Json>;
    jobDescription(filePath: string): Promise<Json>;
  };

  llm: {
    chat(
      prompt: string,
      options?: {
        model?: "chinda-qwen3-4b" | "deepseek-reasoner" | "deepseek-chat" | "deepseek-v4-flash" | "deepseek-v4-pro";
        systemPrompt?: string;
        messages?: Array<{ role: string; content: string }>;
        maxTokens?: number;
        temperature?: number;
      }
    ): Promise<Json>;
    thanoyLegalQa(query: string): Promise<Json>;
  };

  nlp: {
    translate(text: string, sourceLang: string, targetLang: string, options?: { maxLength?: number }): Promise<Json>;
    summarize(text: string, options?: { style?: "standard" | "clarify" | "friendly"; language?: "th" | "en"; maxOutputTokens?: number }): Promise<Json>;
    sentiment(text: string): Promise<Json>;
    toxicity(text: string): Promise<Json>;
    qa(question: string, document: string): Promise<Json>;
    questionGeneration(text: string): Promise<Json>;
  };

  speech: {
    transcribe(filePath: string, options?: { language?: "th" | "en" | "zh"; quality?: "base" | "pro"; chunkSize?: number }): Promise<Json>;
    tts(text: string, outputPath: string, options?: { voice?: "kaitom-v3" | "kaitom-v2" | "kaitom-v1" | "cee"; speed?: number }): Promise<string>;
    voiceClone(text: string, refAudioPath: string, refText: string, outputPath: string): Promise<string>;
    aiAudioDetection(audioPath: string): Promise<Json>;
  };

  image: {
    generate(prompt: string, outputPath: string, options?: { model?: "nanobanana" | "nanobanana-pro" }): Promise<{ path: string; notes: string }>;
    removeBackground(filePath: string, outputPath: string): Promise<string>;
  };

  video: {
    submit(
      prompt: string,
      options?: {
        model?: "seedance" | "seedance-fast";
        duration?: number;
        ratio?: string;
        resolution?: "480p" | "720p" | "1080p";
        generateAudio?: boolean;
        watermark?: boolean;
        firstFrameImageUrl?: string;
        referenceImageUrl?: string;
      }
    ): Promise<Json>;
    status(taskId: string): Promise<Json>;
  };

  smartcity: {
    licensePlate(filePath: string): Promise<Json>;
    meter(filePath: string): Promise<Json>;
    routeOptimization(options: {
      originAddress: string;
      originLatitude: number;
      originLongitude: number;
      stops: Array<Json>;
      driverCount?: number;
    }): Promise<Json>;
  };

  data: {
    thaiHolidays(options?: {
      year?: number;
      startDate?: string;
      endDate?: string;
      daysBefore?: number;
      daysAfter?: number;
      holidayType?: "public" | "financial" | "both";
    }): Promise<Json>;
  };
}

/** Legacy v1.x SDK class (default export). */
declare class iapp_ai {
  constructor(apikey: string);
  apikey: string;
  [method: string]: any;
}

declare namespace iapp_ai {
  export { IAppClient, IAppError };
  export const API_BASE: string;
}

export = iapp_ai;
