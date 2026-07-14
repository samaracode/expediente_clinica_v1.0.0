"use client";

import {
  askAssistant,
  AssistantMessage,
  ApiError,
} from "@/lib/api";
import React, { useEffect, useRef, useState } from "react";

/**
 * "Ask AI" — asistente conversacional de solo lectura para consultar el
 * expediente. Botón flotante (abajo a la derecha) que abre un panel de chat
 * disponible en todas las páginas del área admin.
 *
 * Estados especiales del backend:
 *  - reason "budget_exceeded": se alcanzó el tope de gasto mensual → se muestra
 *    el mensaje y se deshabilita el input hasta que el admin lo reactive.
 *  - reason "not_configured": falta la ANTHROPIC_API_KEY.
 */

interface ChatMessage extends AssistantMessage {
  /** marca de mensajes que son avisos del sistema (no cuentan como historial). */
  system?: boolean;
}

export default function AssistantWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [locked, setLocked] = useState(false); // presupuesto agotado / no configurado
  const [model, setModel] = useState<string | null>(null); // nombre del modelo activo
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  const send = async () => {
    const text = input.trim();
    if (!text || loading || locked) return;

    // Historial real (sin los avisos del sistema) para enviar al backend.
    const history: AssistantMessage[] = messages
      .filter((m) => !m.system)
      .map(({ role, content }) => ({ role, content }));
    const outgoing: AssistantMessage = { role: "user", content: text };

    setMessages((prev) => [...prev, outgoing]);
    setInput("");
    setLoading(true);

    try {
      const res = await askAssistant([...history, outgoing]);
      if (res.model) {
        setModel(res.model);
      }
      if (res.disabled) {
        // "provider_error" es transitorio (rate limit, sin saldo momentáneo,
        // etc.): el usuario puede reintentar, así que NO se bloquea el input.
        // "budget_exceeded" y "not_configured" requieren intervención del
        // administrador, así que sí se bloquea hasta recargar la página.
        if (res.reason !== "provider_error") {
          setLocked(true);
        }
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: res.reply, system: true },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: res.reply },
        ]);
      }
    } catch (e) {
      const msg =
        e instanceof ApiError
          ? e.message
          : "No se pudo contactar al asistente. Intenta de nuevo.";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: msg, system: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <>
      {/* Botón flotante */}
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label="Asistente de ayuda"
        className="fixed bottom-6 right-6 z-99999 flex h-14 w-14 items-center justify-center rounded-full bg-brand-500 text-white shadow-theme-lg transition hover:bg-brand-600 focus:outline-hidden focus:ring-3 focus:ring-brand-500/30"
      >
        {open ? (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path
              d="M6 6l12 12M18 6L6 18"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 3C7.03 3 3 6.58 3 11c0 2.03.86 3.88 2.28 5.28-.1 1.17-.5 2.3-1.1 3.22a.5.5 0 00.55.76 8.1 8.1 0 003.4-1.35c1.16.44 2.45.69 3.87.69 4.97 0 9-3.58 9-8s-4.03-8-9-8z"
              fill="currentColor"
            />
          </svg>
        )}
      </button>

      {/* Panel de chat */}
      <div
        className={`fixed bottom-24 right-6 z-99999 flex w-[calc(100vw-3rem)] max-w-96 flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-theme-lg transition-all dark:border-gray-800 dark:bg-gray-900 ${
          open ? "pointer-events-auto opacity-100" : "pointer-events-none translate-y-2 opacity-0"
        }`}
        style={{ height: "min(32rem, calc(100vh - 8rem))" }}
      >
        {/* Header */}
        <div className="flex items-center gap-2 border-b border-gray-200 px-4 py-3 dark:border-gray-800">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-500/10 text-brand-500">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 3C7.03 3 3 6.58 3 11c0 2.03.86 3.88 2.28 5.28-.1 1.17-.5 2.3-1.1 3.22a.5.5 0 00.55.76 8.1 8.1 0 003.4-1.35c1.16.44 2.45.69 3.87.69 4.97 0 9-3.58 9-8s-4.03-8-9-8z"
                fill="currentColor"
              />
            </svg>
          </span>
          <div>
            <p className="text-sm font-semibold text-gray-800 dark:text-white/90">
              Asistente de ayuda
            </p>
            <p className="text-xs text-gray-400">
              {model ? `Usando ${model}` : "Consulta el expediente"}
            </p>
          </div>
        </div>

        {/* Mensajes */}
        <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
          {messages.length === 0 && (
            <p className="text-sm text-gray-400">
              Hazme una pregunta sobre residentes, medicamentos u ocupación. Por
              ejemplo: <span className="italic">&quot;¿Cuántas camas están ocupadas?&quot;</span>
            </p>
          )}
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-3 py-2 text-sm ${
                  m.role === "user"
                    ? "bg-brand-500 text-white"
                    : m.system
                    ? "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400"
                    : "bg-gray-100 text-gray-800 dark:bg-white/[0.05] dark:text-white/90"
                }`}
              >
                {m.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="rounded-2xl bg-gray-100 px-3 py-2 text-sm text-gray-500 dark:bg-white/[0.05] dark:text-gray-400">
                Escribiendo…
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 p-3 dark:border-gray-800">
          <div className="flex items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              rows={1}
              disabled={locked}
              placeholder={
                locked ? "Asistente no disponible" : "Escribe tu pregunta…"
              }
              className="max-h-28 flex-1 resize-none rounded-lg border border-gray-200 bg-transparent px-3 py-2 text-sm text-gray-800 placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/10 disabled:opacity-60 dark:border-gray-800 dark:text-white/90"
            />
            <button
              onClick={send}
              disabled={loading || locked || !input.trim()}
              className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-500 text-white transition hover:bg-brand-600 disabled:opacity-40"
              aria-label="Enviar"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path
                  d="M3 11l18-8-8 18-2-8-8-2z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinejoin="round"
                  fill="none"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
