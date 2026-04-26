/**
 * Server-side base URL for Django (no trailing slash).
 * Used by Next.js route handlers to call `/api/auth/login/` etc.
 */
export function getBackendOrigin() {
  const fromEnv =
    process.env.BACKEND_API_ORIGIN ||
    process.env.DJANGO_API_URL ||
    (process.env.NEXT_PUBLIC_PLATFORM_API_ROOT || "")
      .replace(/\/api\/?$/i, "")
      .trim();
  if (fromEnv) return fromEnv.replace(/\/$/, "");
  return "http://127.0.0.1:8000";
}

export function getAuthLoginUrl() {
  return `${getBackendOrigin()}/api/auth/login/`;
}

export function getAuthRegisterUrl() {
  return `${getBackendOrigin()}/api/auth/register/`;
}
