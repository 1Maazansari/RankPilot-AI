import { z } from "zod";

export type UrlValidation = { ok: true; url: string } | { ok: false; message: string };

const INVALID = "Please enter a valid website URL.";

const urlSchema = z
  .string()
  .trim()
  .min(3)
  .max(2048)
  .transform((value) => (/^https?:\/\//i.test(value) ? value : `https://${value}`))
  .refine((value) => {
    try {
      const parsed = new URL(value);
      if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return false;
      const host = parsed.hostname;
      if (!host.includes(".") || host.endsWith(".")) return false;
      return true;
    } catch {
      return false;
    }
  }, INVALID);

/** Normalizes "example.com" to "https://example.com/" and validates protocol + host. */
export function validateWebsiteUrl(input: string): UrlValidation {
  const parsed = urlSchema.safeParse(input ?? "");
  if (!parsed.success) return { ok: false, message: INVALID };
  return { ok: true, url: new URL(parsed.data).toString() };
}
