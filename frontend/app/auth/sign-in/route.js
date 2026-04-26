import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { getAuthLoginUrl } from "../../../lib/authBackend";

const SESSION_MAX_AGE = 60 * 60 * 8;
const ACCESS_MAX_AGE = 60 * 60; /* align with Django JWT_ACCESS_MINUTES default */
const REFRESH_MAX_AGE = 60 * 60 * 24 * 7;

function redirectWithError(request, message) {
  const url = new URL("/", request.url);
  url.searchParams.set("error", message);
  return NextResponse.redirect(url, 303);
}

export async function POST(request) {
  const formData = await request.formData();
  const username = String(formData.get("username") || "").trim();
  const password = String(formData.get("password") || "");

  if (!username || !password) {
    return redirectWithError(request, "Enter both username and password.");
  }

  let res;
  try {
    res = await fetch(getAuthLoginUrl(), {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ username, password }),
      cache: "no-store",
    });
  } catch {
    return redirectWithError(
      request,
      "Cannot reach the login server. Start Django or set BACKEND_API_ORIGIN."
    );
  }

  let data = {};
  try {
    data = await res.json();
  } catch {
    data = {};
  }

  if (!res.ok) {
    const detail =
      typeof data.detail === "string"
        ? data.detail
        : "Invalid username or password.";
    return redirectWithError(request, detail);
  }

  const access = typeof data.access === "string" ? data.access : "";
  const refresh = typeof data.refresh === "string" ? data.refresh : "";
  const resolvedUser =
    typeof data.username === "string" && data.username ? data.username : username;

  if (!access) {
    return redirectWithError(request, "Login response missing token.");
  }

  const cookieStore = await cookies();
  const secure = process.env.NODE_ENV === "production";

  cookieStore.set("mxsense_session", "active", {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_MAX_AGE,
    secure,
  });
  cookieStore.set("mxsense_user", resolvedUser, {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_MAX_AGE,
    secure,
  });
  cookieStore.set("mxsense_access", access, {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: ACCESS_MAX_AGE,
    secure,
  });
  if (refresh) {
    cookieStore.set("mxsense_refresh", refresh, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
      maxAge: REFRESH_MAX_AGE,
      secure,
    });
  }

  return NextResponse.redirect(new URL("/dashboard", request.url), 303);
}
