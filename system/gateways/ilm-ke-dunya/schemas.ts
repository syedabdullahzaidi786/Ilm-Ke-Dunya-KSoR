import { z } from "@panaversity/ksor/gateway";

const page = z.number().int().min(1).optional();
const limit = z.number().int().min(1).max(100).optional();

export const quranInput = z.object({
  surah: z.number().int().min(1).max(114).optional(),
  ayah: z.number().int().min(1).optional(),
});

export const hadithInput = z.object({
  collection: z.string().min(1).optional(),
  number: z.number().int().min(1).optional(),
  search: z.string().min(1).optional(),
  page,
  limit,
});

export const duaInput = z.object({
  search: z.string().min(1).optional(),
  category: z.string().min(1).optional(),
  page,
  limit,
});

export const namesInput = z.object({
  search: z.string().min(1).optional(),
  gender: z.string().min(1).optional(),
  origin: z.string().min(1).optional(),
  page,
  limit,
});

export const asmaInput = z.object({
  number: z.number().int().min(1).max(99).optional(),
  search: z.string().min(1).optional(),
  day: z.number().int().optional(),
});

export const moonInput = z.object({ date: z.string().min(1).optional() });

export const hijriInput = z.object({
  direction: z.enum(["gregorian_to_hijri", "hijri_to_gregorian"]),
  year: z.number().int(),
  month: z.number().int().min(1).max(12),
  day: z.number().int().min(1),
});

export const ilmOutput = z.object({
  ok: z.boolean(),
  data: z.unknown().optional(),
  error: z
    .object({ code: z.string(), message: z.string(), status: z.number().optional() })
    .optional(),
  source: z.object({ api: z.literal("ilm-ke-dunya"), endpoint: z.string() }),
});