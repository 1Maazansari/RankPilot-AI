import type { ScanResponse, StoredScan } from "@/types/scan";

const KEY = "rankx:last-scan";

export function saveScan(url: string, result: ScanResponse): void {
  if (typeof window === "undefined") return;
  const payload: StoredScan = { url, scannedAt: new Date().toISOString(), result };
  try {
    sessionStorage.setItem(KEY, JSON.stringify(payload));
  } catch {
    /* storage unavailable */
  }
}

export function readScan(url?: string): StoredScan | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as StoredScan;
    if (!parsed?.result?.seo?.score) return null;
    if (url && parsed.url !== url) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function hasScan(): boolean {
  return readScan() !== null;
}

export function clearScan(): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.removeItem(KEY);
  } catch {
    /* noop */
  }
}
