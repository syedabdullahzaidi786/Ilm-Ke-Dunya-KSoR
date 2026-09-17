import { READ_ONLY, z, type McpServer } from "@panaversity/ksor/gateway";
import { IlmKeDunyaClient, IlmKeDunyaError } from "./client.ts";
import { asmaInput, duaInput, hadithInput, hijriInput, ilmOutput, moonInput, namesInput, quranInput } from "./schemas.ts";

function result(data: unknown, endpoint: string) {
  return { ok: true, data, source: { api: "ilm-ke-dunya" as const, endpoint } };
}

function failure(error: unknown, endpoint: string) {
  const details = error instanceof IlmKeDunyaError
    ? error.details
    : error && typeof error === "object" && "code" in error && "message" in error
      ? {
          code: String(error.code),
          message: String(error.message),
          ...(typeof error.status === "number" ? { status: error.status } : {}),
        }
      : { code: "invalid_input" as const, message: String(error) };
  return {
    ok: false,
    error: details,
    source: { api: "ilm-ke-dunya" as const, endpoint },
  };
}

function response(value: ReturnType<typeof result> | ReturnType<typeof failure>) {
  return {
    structuredContent: value,
    content: [{ type: "text" as const, text: JSON.stringify(value) }],
  };
}

export function registerIlmKeDunyaTools(server: McpServer, client = new IlmKeDunyaClient()): void {
  server.registerTool("ilm_quran_lookup", {
    title: "Look up Quran content",
    description: "Use for Quran surah catalog questions or a specific ayah. Surah-only lookup is not supported because the upstream API currently fails it.",
    inputSchema: quranInput,
    outputSchema: ilmOutput,
    annotations: READ_ONLY,
  }, async (input) => {
    const endpoint = "/v1/quran";
    if (input.surah !== undefined && input.ayah === undefined) {
      return response(failure({ code: "invalid_input", message: "Provide ayah together with surah; surah-only lookup is unavailable." }, endpoint));
    }
    try { return response(result((await client.quran(input)).data, endpoint)); } catch (error) { return response(failure(error, endpoint)); }
  });

  server.registerTool("ilm_hadith_search", {
    title: "Search Hadith",
    description: "Use for Hadith collection browsing, text search, or a numbered reference within a collection.",
    inputSchema: hadithInput,
    outputSchema: ilmOutput,
    annotations: READ_ONLY,
  }, async (input) => {
    const endpoint = "/v1/hadith";
    if (input.number !== undefined && input.collection === undefined) return response(failure({ code: "invalid_input", message: "collection is required when number is provided." }, endpoint));
    try { return response(result((await client.hadith(input)).data, endpoint)); } catch (error) { return response(failure(error, endpoint)); }
  });

  const simpleTools = [
    ["ilm_dua_search", "Search or browse Duas by text or category.", duaInput, (input: z.infer<typeof duaInput>) => client.duas(input), "/v1/duas"],
    ["ilm_names_search", "Search Islamic names or filter them by gender and origin.", namesInput, (input: z.infer<typeof namesInput>) => client.names(input), "/v1/names"],
    ["ilm_asma_lookup", "Browse, search, or look up one of the 99 Names of Allah.", asmaInput, (input: z.infer<typeof asmaInput>) => client.asma(input), "/v1/asma"],
    ["ilm_moon_today", "Get current or date-specific moon and Hijri calendar information.", moonInput, (input: z.infer<typeof moonInput>) => client.moon(input), "/moon"],
  ] as const;
  for (const [name, description, inputSchema, call, endpoint] of simpleTools) {
    server.registerTool(name, { title: description, description, inputSchema, outputSchema: ilmOutput, annotations: READ_ONLY }, async (input) => {
      try { return response(result((await call(input)).data, endpoint)); } catch (error) { return response(failure(error, endpoint)); }
    });
  }

  server.registerTool("ilm_hijri_convert", {
    title: "Convert Gregorian and Hijri dates",
    description: "Use to convert a Gregorian date to Hijri or a Hijri date to Gregorian.",
    inputSchema: hijriInput,
    outputSchema: ilmOutput,
    annotations: READ_ONLY,
  }, async (input) => {
    const endpoint = input.direction === "gregorian_to_hijri" ? "/moon/hijri" : "/moon/gregorian";
    try { return response(result((await client.convert(input.direction, input)).data, endpoint)); } catch (error) { return response(failure(error, endpoint)); }
  });
}