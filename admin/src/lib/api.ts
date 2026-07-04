import { getToken } from "./token";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "/api/v1";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

/**
 * FastAPI devuelve `detail` como string en errores manuales (HTTPException),
 * pero como una LISTA de objetos {loc, msg, type} en errores de validación
 * de Pydantic (422). Sin esto, el mensaje termina siendo el array crudo y
 * React lo renderiza como "[object Object]".
 */
function extractErrorMessage(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((e) => {
        if (e && typeof e === "object" && "msg" in e) {
          const loc = Array.isArray((e as { loc?: unknown[] }).loc)
            ? (e as { loc: unknown[] }).loc.filter((p) => p !== "body").join(".")
            : "";
          return loc ? `${loc}: ${(e as { msg: string }).msg}` : String((e as { msg: string }).msg);
        }
        return typeof e === "string" ? e : JSON.stringify(e);
      })
      .join("; ");
  }
  return "Error desconocido";
}

/** Header Authorization con el token de sesión, si existe. */
function authHeader(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...authHeader(),
      ...(options.headers ?? {}),
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, extractErrorMessage(body.detail));
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

/**
 * Variante de apiFetch para subir archivos (multipart/form-data).
 * No establece Content-Type para que el navegador lo agregue con el boundary.
 */
export async function apiFetchMultipart<T>(path: string, formData: FormData): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    credentials: "include",
    headers: authHeader(),
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, extractErrorMessage(body.detail));
  }

  return res.json() as Promise<T>;
}
