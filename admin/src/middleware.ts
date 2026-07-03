import { NextRequest, NextResponse } from "next/server";
import { canAccess } from "@/lib/access";
import type { Module } from "@/types";

const PUBLIC_PATHS = ["/signin", "/signup", "/reset-password"];

// Los módulos vienen embebidos en el JWT (ADR 0003): si el admin cambia los
// permisos de alguien, el cambio aplica en el próximo login de esa persona,
// no al instante. El backend igual valida en tiempo real contra la BD en
// cada request (ModuleRequired), así que esto es solo UX de navegación.
function decodeJWT(token: string): { role: string; modules: Module[] } {
  try {
    const payload = token.split(".")[1];
    const decoded = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    const parsed = JSON.parse(decoded) as { role?: string; modules?: Module[] };
    return { role: parsed.role ?? "", modules: parsed.modules ?? [] };
  } catch {
    return { role: "", modules: [] };
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
    const { role, modules } = decodeJWT(token);
    if (!canAccess(pathname, role, modules)) {
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
