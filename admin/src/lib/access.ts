import type { Module } from "@/types";

// Permisos por-usuario (ADR 0003): el acceso a cada módulo lo define la lista
// de módulos habilitados del usuario logueado (User.modules, viene de
// /auth/me), no un mapeo fijo por rol. "admin" siempre viene con todos los
// módulos (ver User.allowed_modules en el backend). Rutas sin match (Dashboard,
// User Profile, Residentes gestionados en /residents pero ver nota abajo) son
// siempre accesibles salvo /admin.
//
// Orden importa: primera regla que matchea gana.
const ROUTE_RULES: Array<{ test: (path: string) => boolean; module?: Module; adminOnly?: boolean }> = [
  { test: (p) => p.startsWith("/admin"), adminOnly: true },
  { test: (p) => /\/finance(\/|$)/.test(p), module: "finance" },
  { test: (p) => /\/medical(\/|$)/.test(p), module: "medical" },
  { test: (p) => /\/therapeutic(\/|$)/.test(p), module: "therapeutic" },
  { test: (p) => /\/social-work(\/|$)/.test(p), module: "social_work" },
  { test: (p) => /\/psychology(\/|$)/.test(p), module: "psychology" },
  { test: (p) => /\/occupational-therapy(\/|$)/.test(p), module: "occupational_therapy" },
  { test: (p) => /^\/residents(\/|$)/.test(p), module: "residents" },
  { test: (p) => /^\/operations(\/|$)/.test(p), module: "operations" },
  { test: (p) => /^\/reports(\/|$)/.test(p), module: "reports" },
];

/**
 * @param path Ruta solicitada.
 * @param role Rol del usuario (solo se usa para el atajo admin).
 * @param modules Módulos habilitados del usuario (User.modules de /auth/me).
 */
export function canAccess(path: string, role: string, modules: Module[] = []): boolean {
  if (role === "admin") return true;
  for (const rule of ROUTE_RULES) {
    if (rule.test(path)) {
      if (rule.adminOnly) return false; // ya se descartó admin arriba
      return rule.module ? modules.includes(rule.module) : true;
    }
  }
  return true;
}
