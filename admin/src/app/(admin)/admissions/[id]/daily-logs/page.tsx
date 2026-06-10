"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type { DailyLogOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const INTERVENTION_TYPES = [
  { value: "", label: "— Tipo de intervención —" },
  { value: "individual", label: "Individual" },
  { value: "group", label: "Grupal" },
  { value: "family", label: "Familiar" },
  { value: "medical", label: "Médica" },
  { value: "occupational", label: "Ocupacional" },
  { value: "administrative", label: "Administrativa" },
  { value: "crisis", label: "Crisis" },
  { value: "other", label: "Otro" },
];

type NewLogForm = {
  log_date: string;
  intervention_type: string;
  notes: string;
  recommendations: string;
};

function emptyForm(): NewLogForm {
  const today = new Date().toISOString().slice(0, 10);
  return { log_date: today, intervention_type: "", notes: "", recommendations: "" };
}

const inputCls =
  "w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">{label}</label>
      {children}
    </div>
  );
}

function LogCard({
  log,
  admissionId,
  onUpdate,
}: {
  log: DailyLogOut;
  admissionId: string;
  onUpdate: (updated: DailyLogOut) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [interventionType, setInterventionType] = useState(log.intervention_type ?? "");
  const [notes, setNotes] = useState(log.notes ?? "");
  const [recommendations, setRecommendations] = useState(log.recommendations ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      const updated = await apiFetch<DailyLogOut>(
        `/admissions/${admissionId}/daily-logs/${log.id}`,
        {
          method: "PUT",
          body: JSON.stringify({
            intervention_type: interventionType || null,
            notes: notes || null,
            recommendations: recommendations || null,
          }),
        }
      );
      onUpdate(updated);
      setEditing(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  }

  const typeLabel =
    INTERVENTION_TYPES.find((t) => t.value === (log.intervention_type ?? ""))?.label ?? log.intervention_type;

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-gray-800 dark:text-white">
            {new Date(log.log_date + "T12:00:00").toLocaleDateString("es-CR", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </span>
          {log.intervention_type && (
            <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-400">
              {typeLabel}
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={() => setEditing((v) => !v)}
          className="text-xs text-brand-500 hover:underline"
        >
          {editing ? "Cancelar" : "Editar"}
        </button>
      </div>

      {editing ? (
        <div className="space-y-3">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Field label="Tipo de intervención">
              <select value={interventionType} onChange={(e) => setInterventionType(e.target.value)} className={inputCls}>
                {INTERVENTION_TYPES.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </Field>
          </div>
          <Field label="Notas">
            <textarea rows={4} value={notes} onChange={(e) => setNotes(e.target.value)} className={inputCls} />
          </Field>
          <Field label="Recomendaciones">
            <textarea rows={2} value={recommendations} onChange={(e) => setRecommendations(e.target.value)} className={inputCls} />
          </Field>
          <div className="flex items-center gap-3">
            {error && <p role="alert" className="text-xs text-error-500">{error}</p>}
            <Button size="sm" onClick={handleSave} disabled={saving} className="ml-auto">
              {saving ? "Guardando..." : "Guardar"}
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          {log.notes && (
            <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{log.notes}</p>
          )}
          {log.recommendations && (
            <div className="mt-2 rounded-lg bg-brand-50 px-3 py-2 dark:bg-brand-900/10">
              <p className="text-xs font-medium text-brand-700 dark:text-brand-400 mb-0.5">Recomendaciones</p>
              <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{log.recommendations}</p>
            </div>
          )}
          {!log.notes && !log.recommendations && (
            <p className="text-sm text-gray-400 italic">Sin contenido</p>
          )}
        </div>
      )}
    </div>
  );
}

export default function DailyLogsPage() {
  const { id } = useParams<{ id: string }>();
  const [logs, setLogs] = useState<DailyLogOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<NewLogForm>(emptyForm());
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (fromDate) params.set("from_date", fromDate);
    if (toDate) params.set("to_date", toDate);
    const qs = params.toString() ? `?${params}` : "";
    apiFetch<DailyLogOut[]>(`/admissions/${id}/daily-logs${qs}`)
      .then(setLogs)
      .finally(() => setLoading(false));
  }, [id, fromDate, toDate]);

  function setField<K extends keyof NewLogForm>(field: K, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleCreate() {
    if (!form.log_date) {
      setCreateError("La fecha es obligatoria.");
      return;
    }
    setCreating(true);
    setCreateError(null);
    try {
      const created = await apiFetch<DailyLogOut>(`/admissions/${id}/daily-logs`, {
        method: "POST",
        body: JSON.stringify({
          log_date: form.log_date,
          intervention_type: form.intervention_type || null,
          notes: form.notes || null,
          recommendations: form.recommendations || null,
        }),
      });
      setLogs((prev) => [created, ...prev]);
      setForm(emptyForm());
      setShowForm(false);
    } catch (err) {
      setCreateError(err instanceof ApiError ? err.message : "Error al crear");
    } finally {
      setCreating(false);
    }
  }

  function handleUpdate(updated: DailyLogOut) {
    setLogs((prev) => prev.map((l) => (l.id === updated.id ? updated : l)));
  }

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Notas diarias" />

      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Notas diarias</h2>
            <p className="text-sm text-gray-500">
              <Link href={`/admissions/${id}`} className="text-brand-500 hover:underline">
                Admisión #{id}
              </Link>
            </p>
          </div>
          <div className="flex flex-wrap items-end gap-3">
            <div>
              <label className="mb-1 block text-xs text-gray-400">Desde</label>
              <input
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
                className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-gray-400">Hasta</label>
              <input
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
                className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
              />
            </div>
            {(fromDate || toDate) && (
              <button
                type="button"
                onClick={() => { setFromDate(""); setToDate(""); }}
                className="text-xs text-gray-400 hover:text-gray-600"
              >
                Limpiar
              </button>
            )}
            <Button onClick={() => { setShowForm((v) => !v); setCreateError(null); }}>
              {showForm ? "Cancelar" : "Nueva nota"}
            </Button>
          </div>
        </div>
      </div>

      {/* Creation form */}
      {showForm && (
        <div className="rounded-2xl border border-brand-200 bg-white p-6 space-y-5 dark:border-brand-800/50 dark:bg-white/[0.03]">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">Nueva nota</h3>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <Field label="Fecha *">
              <input type="date" value={form.log_date} onChange={(e) => setField("log_date", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Tipo de intervención">
              <select value={form.intervention_type} onChange={(e) => setField("intervention_type", e.target.value)} className={inputCls}>
                {INTERVENTION_TYPES.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </Field>
            <div className="sm:col-span-2">
              <Field label="Notas">
                <textarea rows={4} value={form.notes} onChange={(e) => setField("notes", e.target.value)} placeholder="Observaciones, evolución, intervenciones realizadas..." className={inputCls} />
              </Field>
            </div>
            <div className="sm:col-span-2">
              <Field label="Recomendaciones">
                <textarea rows={2} value={form.recommendations} onChange={(e) => setField("recommendations", e.target.value)} placeholder="Recomendaciones para el equipo..." className={inputCls} />
              </Field>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {createError && <p role="alert" className="text-sm text-error-500">{createError}</p>}
            <Button onClick={handleCreate} disabled={creating} className="ml-auto">
              {creating ? "Guardando..." : "Crear nota"}
            </Button>
          </div>
        </div>
      )}

      {/* List */}
      {loading ? (
        <div className="text-sm text-gray-400">Cargando...</div>
      ) : logs.length === 0 ? (
        <div className="rounded-2xl border border-gray-200 bg-white p-10 text-center dark:border-gray-800 dark:bg-white/[0.03]">
          <p className="text-sm text-gray-400">Sin notas registradas.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {logs.map((log) => (
            <LogCard key={log.id} log={log} admissionId={id} onUpdate={handleUpdate} />
          ))}
        </div>
      )}
    </div>
  );
}
