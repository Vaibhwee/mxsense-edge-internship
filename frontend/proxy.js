import { NextResponse } from "next/server";

const PROTECTED_PREFIXES = ["/dashboard", "/locations", "/modules"];

export function proxy(request) {
  const { pathname } = request.nextUrl;
  const hasSession = request.cookies.get("mxsense_session")?.value === "active";

  const needsAuth = PROTECTED_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
  );

  if (needsAuth && !hasSession) {
    const login = new URL("/", request.url);
    login.searchParams.set("error", "Please sign in to continue.");
    return NextResponse.redirect(login);
  }

  if ((pathname === "/" || pathname === "/sign-up") && hasSession) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/",
    "/sign-up",
    "/dashboard/:path*",
    "/locations/:path*",
    "/modules/:path*",
  ],
};
