import { NextRequest, NextResponse } from "next/server";
import { canAccess } from "@/lib/access";

const PUBLIC_PATHS = ["/signin", "/signup", "/reset-password"];

function decodeJWTRole(token: string): string {
  try {
    const payload = token.split(".")[1];
    const decoded = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return (JSON.parse(decoded) as { role?: string }).role ?? "";
  } catch {
    return "";
  }
}

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  const isPublic = PUBLIC_PATHS.some((p) => pathname.startsWith(p));
  const token = req.cookies.get("access_token")?.value;

  if (!isPublic && !token) {
    const url = req.nextUrl.clone();
    url.pathname = "/signin";
    return NextResponse.redirect(url);
  }

  if (isPublic && token) {
    const url = req.nextUrl.clone();
    url.pathname = "/";
    return NextResponse.redirect(url);
  }

  if (token && pathname !== "/unauthorized") {
    const role = decodeJWTRole(token);
    if (!canAccess(pathname, role)) {
      const url = req.nextUrl.clone();
      url.pathname = "/unauthorized";
      return NextResponse.redirect(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|images|favicon.ico).*)"],
};
