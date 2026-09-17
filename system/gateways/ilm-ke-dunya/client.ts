import { z } from "@panaversity/ksor/gateway";

export const DEFAULT_BASE_URL = "https://ilm-ke-dunya-api.vercel.app/api";

const envelopeSchema = z.object({
  error: z.string().nullable().optional(),
  data: z.unknown().nullable(),
  msg: z.string().optional(),
});

export type IlmErrorCode =
  | "invalid_input"
  | "upstream_http_error"
  | "upstream_api_error"
  | "invalid_upstream_response"
  | "upstream_timeout"
  | "upstream_network_error";

export interface IlmApiError {
  code: IlmErrorCode;
  message: string;
  status?: number;
}

export interface IlmApiResult {
  data: unknown;
  msg?: string;
}

export class IlmKeDunyaError extends Error {
  readonly details: IlmApiError;

  constructor(details: IlmApiError) {
    super(details.message);
    this.details = details;
    this.name = "IlmKeDunyaError";
  }
}

function baseUrl(): string {
  return (process.env.ILM_KE_DUNYA_API_BASE_URL ?? DEFAULT_BASE_URL).replace(/\/$/, "");
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === "AbortError";
}

export class IlmKeDunyaClient {
  private readonly options: { baseUrl?: string; timeoutMs?: number };

  constructor(options: { baseUrl?: string; timeoutMs?: number } = {}) {
    this.options = options;
  }

  async get(path: string, params: Record<string, string | number | undefined> = {}): Promise<IlmApiResult> {
    const url = new URL(`${this.options.baseUrl ?? baseUrl()}${path}`);
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) url.searchParams.set(key, String(value));
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.options.timeoutMs ?? 10000);

    let response: Response;
    try {
      response = await fetch(url, { method: "GET", signal: controller.signal });
    } catch (error) {
      if (isAbortError(error)) {
        throw new IlmKeDunyaError({
          code: "upstream_timeout",
          message: "The Ilm Ke Dunya API request timed out.",
        });
      }
      throw new IlmKeDunyaError({
        code: "upstream_network_error",
        message: "The Ilm Ke Dunya API could not be reached.",
      });
    } finally {
      clearTimeout(timeout);
    }

    let payload: unknown;
    try {
      payload = await response.json();
    } catch {
      throw new IlmKeDunyaError({
        code: "invalid_upstream_response",
        message: "The Ilm Ke Dunya API returned malformed JSON.",
        status: response.status,
      });
    }

    if (!response.ok) {
      throw new IlmKeDunyaError({
        code: "upstream_http_error",
        message: `The Ilm Ke Dunya API returned HTTP ${response.status}.`,
        status: response.status,
      });
    }

    const parsed = envelopeSchema.safeParse(payload);
    if (!parsed.success) {
      throw new IlmKeDunyaError({
        code: "invalid_upstream_response",
        message: "The Ilm Ke Dunya API returned an unexpected response shape.",
        status: response.status,
      });
    }

    if (parsed.data.error || (parsed.data.data && typeof parsed.data.data === "object" && "error" in parsed.data.data)) {
      const nestedError =
        parsed.data.data && typeof parsed.data.data === "object" && "error" in parsed.data.data
          ? String(parsed.data.data.error)
          : parsed.data.error;
      throw new IlmKeDunyaError({
        code: "upstream_api_error",
        message: nestedError || parsed.data.msg || "The Ilm Ke Dunya API returned an error.",
        status: response.status,
      });
    }

    return { data: parsed.data.data, msg: parsed.data.msg };
  }

  quran(params: { surah?: number; ayah?: number }) {
    return this.get("/v1/quran", params);
  }

  hadith(params: { collection?: string; number?: number; search?: string; page?: number; limit?: number }) {
    return this.get("/v1/hadith", params);
  }

  duas(params: { search?: string; category?: string; page?: number; limit?: number }) {
    return this.get("/v1/duas", params);
  }

  names(params: { search?: string; gender?: string; origin?: string; page?: number; limit?: number }) {
    return this.get("/v1/names", params);
  }

  asma(params: { number?: number; search?: string; day?: number }) {
    return this.get("/v1/asma", params);
  }

  moon(params: { date?: string }) {
    return this.get("/moon", params);
  }

  convert(direction: "gregorian_to_hijri" | "hijri_to_gregorian", params: { year: number; month: number; day: number }) {
    return this.get(direction === "gregorian_to_hijri" ? "/moon/hijri" : "/moon/gregorian", params);
  }
}