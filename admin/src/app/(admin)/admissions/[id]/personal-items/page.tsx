"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type { PersonalItem, PersonalItemsInventoryOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const CONDITION_OPTIONS = [
  { value: "", label: "— Sin especificar —" },
  { value: "bueno", label: "Bueno" },
  { value: "regular", label: "Regular" },
  { value: "deteriorado", label: "Deteriorado" },
];

function emptyItem(): PersonalItem {
  return { description: "", quantity: 1, condition: null };
}

export default function PersonalItemsPage() {
  const { id } = useParams<{ id: string }>();
  const [items, setItems] = useState<PersonalItem[]>([emptyItem()]);
  const [notes, setNotes] = useState("");
  const [recordedAt, setRecordedAt] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<PersonalItemsInventoryOut>(`/admissions/${id}/personal-items`)
      .then((data) => {
        setItems(data.items.length > 0 ? data.items : [emptyItem()]);
        setNotes(data.notes ?? "");
        setRecordedAt(data.recorded_at);
      })
      .finally(() => setLoading(false));
  }, [id]);

  function updateItem(index: number, field: keyof PersonalItem, value: string | number | null) {
    setItems((prev) => prev.map((item, i) => i === index ? { ...item, [field]: value } : item));
    setSaved(false);
  }

  function addItem() {
    setItems((prev) => [...prev, emptyItem()]);
    setSaved(false);
  }

  function removeItem(index: number) {
    setItems((prev) => prev.filter((_, i) => i !== index));
    setSaved(false);
  }

  async function handleSave() {
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      const validItems = items.filter((item) => item.description.trim() !== "");
      const data = await apiFetch<PersonalItemsInventoryOut>(
        `/admissions/${id}/personal-items`,
        {
          method: "PUT",
          body: JSON.stringify({ items: validItems, notes: notes || null }),
        }
      );
      setItems(data.items.length > 0 ? data.items : [emptyItem()]);
      setNotes(data.notes ?? "");
      setRecordedAt(data.recorded_at);
      setSaved(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Inventario de pertenencias" />

      {/* Header */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
              Inventario de pertenencias personales
            </h2>
            <p className="text-sm text-gray-500">
              <Link href={`/admissions/${id}`} className="text-brand-500 hover:underline">
                Admisión #{id}
              </Link>
            </p>
          </div>
          {recordedAt && (
            <p className="text-xs text-gray-400">
              Última actualización:{" "}
              {new Date(recordedAt).toLocaleDateString("es-CR", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-sm text-gray-400">Cargando...</div>
      ) : (
        <>
          {/* Tabla de artículos */}
          <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="border-b border-gray-100 dark:border-gray-800">
                  <tr className="bg-gray-50 dark:bg-gray-800/50">
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 w-full">
                      Descripción del artículo
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 whitespace-nowrap">
                      Cantidad
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 whitespace-nowrap">
                      Estado
                    </th>
                    <th className="px-4 py-3 w-10" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {items.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50/50 dark:hover:bg-white/[0.01]">
                      <td className="px-4 py-2">
                        <input
                          type="text"
                          value={item.description}
                          onChange={(e) => updateItem(index, "description", e.target.value)}
                          placeholder="Ej: Camisa azul, zapatos tenis..."
                          className="w-full rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
                        />
                      </td>
                      <td className="px-4 py-2">
                        <input
                          type="number"
                          min={1}
                          value={item.quantity}
                          onChange={(e) => updateItem(index, "quantity", Math.max(1, parseInt(e.target.value) || 1))}
                          className="w-20 rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
                        />
                      </td>
                      <td className="px-4 py-2">
                        <select
                          value={item.condition ?? ""}
                          onChange={(e) => updateItem(index, "condition", e.target.value || null)}
                          className="rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
                        >
                          {CONDITION_OPTIONS.map((opt) => (
                            <option key={opt.value} value={opt.value}>{opt.label}</option>
                          ))}
                        </select>
                      </td>
                      <td className="px-4 py-2 text-center">
                        <button
                          type="button"
                          onClick={() => removeItem(index)}
                          disabled={items.length === 1}
                          className="text-gray-300 hover:text-error-500 disabled:cursor-not-allowed disabled:opacity-30 transition-colors"
                          aria-label="Eliminar fila"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="px-4 py-3 border-t border-gray-100 dark:border-gray-800">
              <button
                type="button"
                onClick={addItem}
                className="text-sm text-brand-500 hover:text-brand-600 font-medium"
              >
                + Agregar artículo
              </button>
            </div>
          </div>

          {/* Observaciones */}
          <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
            <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Observaciones generales
            </label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => { setNotes(e.target.value); setSaved(false); }}
              placeholder="Notas sobre el estado general de las pertenencias, artículos no permitidos, etc."
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
            />
          </div>

          {/* Acciones */}
          <div className="flex items-center justify-between">
            <div>
              {error && <p role="alert" className="text-sm text-error-500">{error}</p>}
              {saved && <p className="text-sm text-success-600">Guardado correctamente.</p>}
            </div>
            <Button onClick={handleSave} disabled={saving}>
              {saving ? "Guardando..." : "Guardar inventario"}
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
