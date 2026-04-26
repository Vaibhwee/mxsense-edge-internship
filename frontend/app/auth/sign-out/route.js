import { cookies } from "next/headers";
import { NextResponse } from "next/server";


export async function POST(request) {
  const cookieStore = await cookies();
  cookieStore.delete("mxsense_session");
  cookieStore.delete("mxsense_user");
  cookieStore.delete("mxsense_access");
  cookieStore.delete("mxsense_refresh");

  return NextResponse.redirect(new URL("/", request.url), 303);
}
