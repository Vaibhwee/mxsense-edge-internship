/**
 * Turn API image paths into absolute URLs so <img src> never hits localhost:3000.
 */
export function resolveDisplayImageUrl(src) {
  if (src == null || typeof src !== "string") return null;
  const s = src.trim();
  if (!s) return null;
  if (/^https?:\/\//i.test(s)) return s;
  if (s.startsWith("//")) return `https:${s}`;

  const origin =
    (typeof process !== "undefined" &&
      process.env &&
      (process.env.NEXT_PUBLIC_BACKEND_ORIGIN ||
        process.env.NEXT_PUBLIC_DJANGO_ORIGIN)) ||
    "http://127.0.0.1:8000";
  const base = String(origin).replace(/\/$/, "");

  if (s.startsWith("/")) {
    return base + s;
  }

  return `${base}/media/${s.replace(/^\/+/, "")}`;
}
