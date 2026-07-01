/**
 * Manejo del token de sesión en el cliente.
 *
 * En producción el frontend (Vercel) y la API (Render) viven en dominios
 * distintos, así que la cookie httpOnly de la API no viaja al frontend.
 * Guardamos el token que devuelve /auth/login aquí y lo mandamos como
 * header Authorization: Bearer en cada petición.
 *
 * Se guarda en una cookie (para que el middleware de Next, que corre en el
 * servidor, pueda leerla) y también en memoria para acceso rápido.
 */

const TOKEN_COOKIE = "access_token";
// 8 horas, igual que ACCESS_TOKEN_EXPIRE_MINUTES del backend.
const MAX_AGE_SECONDS = 8 * 60 * 60;

export function setToken(token: string): void {
  if (typeof document === "undefined") return;
  const secure = window.location.protocol === "https:" ? "; Secure" : "";
  // SameSite=Lax: la cookie es del propio dominio de Vercel, no cross-site.
  document.cookie = `${TOKEN_COOKIE}=${token}; Path=/; Max-Age=${MAX_AGE_SECONDS}; SameSite=Lax${secure}`;
}

export function getToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${TOKEN_COOKIE}=`));
  return match ? decodeURIComponent(match.split("=")[1]) : null;
}

export function clearToken(): void {
  if (typeof document === "undefined") return;
  document.cookie = `${TOKEN_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax`;
}
