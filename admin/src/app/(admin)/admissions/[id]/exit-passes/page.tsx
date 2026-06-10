"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type { ExitPassOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const PASS_TYPES = [
  { value: "regular", label: "Regular" },
  { value: "special", label: "Especial" },
];

const PASS_STATUSES = [
  { value: "pending", label: "Pendiente" },
  { value: "approved", label: "Aprobado" },
  { value: "rejected", label: "Rechazado" },
  { value: "completed", label: "Completado" },
];

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-warning-50 text-warning-700 dark:bg-warning-900/20 dark:text-warning-400",
  approved: "bg-brand-50 text-brand-700 dark:bg-brand-900/20 dark:text-brand-400",
  rejected: "bg-error-50 text-error-700 dark:bg-error-900/20 dark:text-error-400",
  completed: "bg-success-50 text-success-700 dark:bg-success-900/20 dark:text-success-400",
};

const TYPE_COLORS: Record<string, string> = {
  regular: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  special: "bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-400",
};

type NewPassForm = {
  departure_date: string;
  return_date_expected: string;
  reason: string;
  companion: string;
  narrative: string;
  pass_type: string;
};

function emptyForm(): NewPassForm {
  return {
    departure_date: "",
    return_date_expected: "",
    reason: "",
    companion: "",
    narrative: "",
    pass_type: "regular",
  };
}

function formatDT(dt: string | null): string {
  if (!dt) return "—";
  return new Date(dt).toLocaleString("es-CR", { dateStyle: "short", timeStyle: "short" });
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

function PassCard({
  pass,
  admissionId,
  onUpdate,
}: {
  pass: ExitPassOut;
  admissionId: string;
  onUpdate: (updated: ExitPassOut) => void;
}) {
  const [status, setStatus] = useState(pass.status);
  const [returnActual, setReturnActual] = useState(pass.return_date_actual ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleUpdate() {
    setSaving(true);
    setError(null);
    try {
      const updated = await apiFetch<ExitPassOut>(
        `/admissions/${admissionId}/exit-passes/${pass.id}`,
        {
          method: "PUT",
          body: JSON.stringify({
            status,
            return_date_actual: returnActual || null,
          }),
        }
      );
      onUpdate(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  }

  const hasChanges = status !== pass.status || returnActual !== (pass.return_date_actual ?? "");

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
      {/* Header */}
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${TYPE_COLORS[pass.pass_type] ?? TYPE_COLORS.regular}`}>
          {PASS_TYPES.find((t) => t.value === pass.pass_type)?.label ?? pass.pass_type}
        </span>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLORS[pass.status] ?? STATUS_COLORS.pending}`}>
          {PASS_STATUSES.find((s) => s.value === pass.status)?.label ?? pass.status}
        </span>
        <span className="ml-auto text-xs text-gray-400">
          Solicitado: {formatDT(pass.requested_at)}
        </span>
      </div>

      {/* Details */}
      <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm mb-4 sm:grid-cols-4">
        <div>
          <dt className="text-gray-400">Salida</dt>
          <dd className="text-gray-700 dark:text-white font-medium">{formatDT(pass.departure_date)}</dd>
        </div>
        <div>
          <dt className="text-gray-400">Regreso esperado</dt>
          <dd className="text-gray-700 dark:text-white font-medium">{formatDT(pass.return_date_expected)}</dd>
        </div>
        <div>
          <dt className="text-gray-400">Regreso real</dt>
          <dd className="text-gray-700 dark:text-white font-medium">{formatDT(pass.return_date_actual)}</dd>
        </div>
        {pass.companion && (
          <div>
            <dt className="text-gray-400">Acompañante</dt>
            <dd className="text-gray-700 dark:text-white">{pass.companion}</dd>
          </div>
        )}
      </dl>

      {pass.reason && (
        <p className="text-sm text-gray-600 dark:text-gray-300 mb-4 border-t border-gray-100 pt-3 dark:border-gray-800">
          {pass.reason}
        </p>
      )}

      {/* Quick update */}
      <div className="border-t border-gray-100 pt-4 dark:border-gray-800">
        <div className="flex flex-wrap items-end gap-3">
          <div className="flex-1 min-w-[140px]">
            <Field label="Actualizar estado">
              <select value={status} onChange={(e) => setStatus(e.target.value)} className={inputCls}>
                {PASS_STATUSES.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </Field>
          </div>
          <div className="flex-1 min-w-[180px]">
            <Field label="Fecha de regreso real">
              <input
                type="datetime-local"
                value={returnActual}
                onChange={(e) => setReturnActual(e.target.value)}
                className={inputCls}
              />
            </Field>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleUpdate}
            disabled={saving || !hasChanges}
          >
            {saving ? "Guardando..." : "Guardar"}
          </Button>
        </div>
        {error && <p role="alert" className="mt-1 text-xs text-error-500">{error}</p>}
      </div>
    </div>
  );
}

export default function ExitPassesPage() {
  const { id } = useParams<{ id: string }>();
  const [passes, setPasses] = useState<ExitPassOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<NewPassForm>(emptyForm());
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<ExitPassOut[]>(`/admissions/${id}/exit-passes`)
      .then(setPasses)
      .finally(() => setLoading(false));
  }, [id]);

  function setField<K extends keyof NewPassForm>(field: K, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleCreate() {
    if (!form.departure_date) {
      setCreateError("La fecha de salida es obligatoria.");
      return;
    }
    setCreating(true);
    setCreateError(null);
    try {
      const created = await apiFetch<ExitPassOut>(`/admissions/${id}/exit-passes`, {
        method: "POST",
        body: JSON.stringify({
          departure_date: form.departure_date || null,
          return_date_expected: form.return_date_expected || null,
          reason: form.reason || null,
          companion: form.companion || null,
          narrative: form.narrative || null,
          pass_type: form.pass_type,
        }),
      });
      setPasses((prev) => [created, ...prev]);
      setForm(emptyForm());
      setShowForm(false);
    } catch (err) {
      setCreateError(err instanceof ApiError ? err.message : "Error al crear");
    } finally {
      setCreating(false);
    }
  }

  function handleUpdate(updated: ExitPassOut) {
    setPasses((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
  }

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Permisos de salida" />

      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Permisos de salida</h2>
            <p className="text-sm text-gray-500">
              <Link href={`/admissions/${id}`} className="text-brand-500 hover:underline">
                Admisión #{id}
              </Link>
            </p>
          </div>
          <Button onClick={() => { setShowForm((v) => !v); setCreateError(null); }}>
            {showForm ? "Cancelar" : "Nueva solicitud"}
          </Button>
        </div>
      </div>

      {/* Creation form */}
      {showForm && (
        <div className="rounded-2xl border border-brand-200 bg-white p-6 space-y-5 dark:border-brand-800/50 dark:bg-white/[0.03]">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
            Nueva solicitud de permiso
          </h3>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <Field label="Tipo de permiso">
              <select value={form.pass_type} onChange={(e) => setField("pass_type", e.target.value)} className={inputCls}>
                {PASS_TYPES.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </Field>
            <Field label="Fecha y hora de salida *">
              <input type="datetime-local" value={form.departure_date} onChange={(e) => setField("departure_date", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Regreso esperado">
              <input type="datetime-local" value={form.return_date_expected} onChange={(e) => setField("return_date_expected", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Acompañante">
              <input type="text" value={form.companion} onChange={(e) => setField("companion", e.target.value)} placeholder="Nombre del acompañante" className={inputCls} />
            </Field>
            <div className="sm:col-span-2">
              <Field label="Motivo">
                <textarea rows={2} value={form.reason} onChange={(e) => setField("reason", e.target.value)} placeholder="Motivo del permiso..." className={inputCls} />
              </Field>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {createError && <p role="alert" className="text-sm text-error-500">{createError}</p>}
            <Button onClick={handleCreate} disabled={creating} className="ml-auto">
              {creating ? "Guardando..." : "Crear solicitud"}
            </Button>
          </div>
        </div>
      )}

      {/* List */}
      {loading ? (
        <div className="text-sm text-gray-400">Cargando...</div>
      ) : passes.length === 0 ? (
        <div className="rounded-2xl border border-gray-200 bg-white p-10 text-center dark:border-gray-800 dark:bg-white/[0.03]">
          <p className="text-sm text-gray-400">Sin permisos registrados.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {passes.map((p) => (
            <PassCard key={p.id} pass={p} admissionId={id} onUpdate={handleUpdate} />
          ))}
        </div>
      )}
    </div>
  );
}
