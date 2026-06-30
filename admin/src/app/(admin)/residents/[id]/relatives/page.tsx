"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type { RelativeOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const MARITAL_STATUS_LABELS: Record<string, string> = {
  single: "Soltero/a",
  married: "Casado/a",
  divorced: "Divorciado/a",
  widowed: "Viudo/a",
  common_law: "Unión libre",
};

const EDUCATION_LABELS: Record<string, string> = {
  none: "Sin estudios",
  primary: "Primaria",
  secondary: "Secundaria",
  technical: "Técnico",
  university: "Universidad",
  postgraduate: "Posgrado",
};

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

type RelativeForm = {
  relation_type: string;
  first_name: string;
  last_name: string;
  id_number: string;
  birthdate: string;
  marital_status: string;
  address: string;
  judicial_situation: string;
  phone: string;
  education_level: string;
};

const EMPTY_FORM: RelativeForm = {
  relation_type: "",
  first_name: "",
  last_name: "",
  id_number: "",
  birthdate: "",
  marital_status: "",
  address: "",
  judicial_situation: "",
  phone: "",
  education_level: "",
};

function RelativeCard({
  relative,
  onUpdate,
  onUnlink,
}: {
  relative: RelativeOut;
  onUpdate: (r: RelativeOut) => void;
  onUnlink: (patientRelativeId: number) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [form, setForm] = useState<RelativeForm>({
    relation_type: relative.relation_type,
    first_name: relative.first_name,
    last_name: relative.last_name,
    id_number: relative.id_number ?? "",
    birthdate: relative.birthdate ?? "",
    marital_status: relative.marital_status ?? "",
    address: relative.address ?? "",
    judicial_situation: relative.judicial_situation ?? "",
    phone: relative.phone ?? "",
    education_level: relative.education_level ?? "",
  });
  const [saving, setSaving] = useState(false);
  const [confirmUnlink, setConfirmUnlink] = useState(false);
  const [unlinking, setUnlinking] = useState(false);

  async function handleUnlink() {
    setUnlinking(true);
    try {
      await apiFetch(`/residents/relatives/${relative.patient_relative_id}`, { method: "DELETE" });
      onUnlink(relative.patient_relative_id);
    } finally {
      setUnlinking(false);
    }
  }

  function setField<K extends keyof RelativeForm>(k: K, v: string) {
    setForm((prev) => ({ ...prev, [k]: v }));
  }

  async function save() {
    setSaving(true);
    try {
      const updated = await apiFetch<RelativeOut>(`/residents/relatives/${relative.patient_relative_id}`, {
        method: "PUT",
        body: JSON.stringify({
          relation_type: form.relation_type || undefined,
          first_name: form.first_name || undefined,
          last_name: form.last_name || undefined,
          id_number: form.id_number || undefined,
          birthdate: form.birthdate || undefined,
          marital_status: form.marital_status || undefined,
          address: form.address || undefined,
          judicial_situation: form.judicial_situation || undefined,
          phone: form.phone || undefined,
          education_level: form.education_level || undefined,
        }),
      });
      onUpdate(updated);
      setExpanded(false);
    } finally {
      setSaving(false);
    }
  }

  const age = relative.birthdate
    ? Math.floor((Date.now() - new Date(relative.birthdate + "T12:00:00").getTime()) / (365.25 * 24 * 3600 * 1000))
    : null;

  return (
    <div className="rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] overflow-hidden">
      <div className="w-full px-5 py-4 flex items-start justify-between hover:bg-gray-50 dark:hover:bg-white/[0.02] transition-colors cursor-pointer"
        onClick={() => setExpanded((v) => !v)}
      >
        <div>
          <p className="font-medium text-gray-800 dark:text-white">
            {relative.first_name} {relative.last_name}
          </p>
          <p className="text-xs text-gray-400 mt-0.5">
            {relative.relation_type}
            {age != null && ` · ${age} años`}
            {relative.phone && ` · ${relative.phone}`}
          </p>
        </div>
        <div className="flex items-center gap-2 mt-1" onClick={(e) => e.stopPropagation()}>
          {confirmUnlink ? (
            <span className="flex items-center gap-1">
              <span className="text-xs text-gray-400">¿Desvincular?</span>
              <button
                type="button"
                onClick={handleUnlink}
                disabled={unlinking}
                className="rounded px-2 py-0.5 text-xs font-medium bg-error-500 text-white hover:bg-error-600 disabled:opacity-50"
              >
                {unlinking ? "..." : "Sí"}
              </button>
              <button
                type="button"
                onClick={() => setConfirmUnlink(false)}
                className="rounded px-2 py-0.5 text-xs border border-gray-300 text-gray-500"
              >
                No
              </button>
            </span>
          ) : (
            <button
              type="button"
              onClick={() => setConfirmUnlink(true)}
              className="text-xs text-error-500 hover:underline"
            >
              Desvincular
            </button>
          )}
          <span className="text-xs text-brand-500">{expanded ? "▲ Cerrar" : "▼ Editar"}</span>
        </div>
      </div>

      {expanded && (
        <div className="px-5 pb-5 border-t border-gray-100 dark:border-gray-800 pt-4 space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Field label="Parentesco">
              <input type="text" value={form.relation_type} onChange={(e) => setField("relation_type", e.target.value)} placeholder="Ej. padre, madre, esposo/a..." className={inputCls} />
            </Field>
            <Field label="Nombre">
              <input type="text" value={form.first_name} onChange={(e) => setField("first_name", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Apellido">
              <input type="text" value={form.last_name} onChange={(e) => setField("last_name", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Cédula">
              <input type="text" value={form.id_number} onChange={(e) => setField("id_number", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Fecha de nacimiento">
              <input type="date" value={form.birthdate} onChange={(e) => setField("birthdate", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Estado civil">
              <select value={form.marital_status} onChange={(e) => setField("marital_status", e.target.value)} className={inputCls}>
                <option value="">— Seleccionar —</option>
                {Object.entries(MARITAL_STATUS_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </Field>
            <Field label="Teléfono">
              <input type="text" value={form.phone} onChange={(e) => setField("phone", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Escolaridad">
              <select value={form.education_level} onChange={(e) => setField("education_level", e.target.value)} className={inputCls}>
                <option value="">— Seleccionar —</option>
                {Object.entries(EDUCATION_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </Field>
            <div className="sm:col-span-2 lg:col-span-1">
              <Field label="Situación judicial">
                <input type="text" value={form.judicial_situation} onChange={(e) => setField("judicial_situation", e.target.value)} placeholder="Sin antecedentes, pendiente..." className={inputCls} />
              </Field>
            </div>
            <div className="sm:col-span-2 lg:col-span-3">
              <Field label="Dirección">
                <input type="text" value={form.address} onChange={(e) => setField("address", e.target.value)} className={inputCls} />
              </Field>
            </div>
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setExpanded(false)} className="text-sm text-gray-400 hover:text-gray-600">Cancelar</button>
            <Button onClick={save} disabled={saving}>{saving ? "Guardando..." : "Guardar cambios"}</Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function RelativesPage() {
  const { id } = useParams<{ id: string }>();
  const [relatives, setRelatives] = useState<RelativeOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<RelativeForm>(EMPTY_FORM);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<RelativeOut[]>(`/residents/${id}/relatives`).then(setRelatives).finally(() => setLoading(false));
  }, [id]);

  function setField<K extends keyof RelativeForm>(k: K, v: string) {
    setForm((prev) => ({ ...prev, [k]: v }));
  }

  async function handleCreate() {
    if (!form.relation_type || !form.first_name || !form.last_name) {
      setCreateError("Parentesco, nombre y apellido son obligatorios.");
      return;
    }
    setCreating(true);
    setCreateError(null);
    try {
      const created = await apiFetch<RelativeOut>(`/residents/${id}/relatives`, {
        method: "POST",
        body: JSON.stringify({
          relation_type: form.relation_type,
          first_name: form.first_name,
          last_name: form.last_name,
          id_number: form.id_number || null,
          birthdate: form.birthdate || null,
          marital_status: form.marital_status || null,
          address: form.address || null,
          judicial_situation: form.judicial_situation || null,
          phone: form.phone || null,
          education_level: form.education_level || null,
        }),
      });
      setRelatives((prev) => [...prev, created]);
      setForm(EMPTY_FORM);
      setShowForm(false);
    } catch (err) {
      setCreateError(err instanceof ApiError ? err.message : "Error al crear familiar");
    } finally {
      setCreating(false);
    }
  }

  function handleUpdate(updated: RelativeOut) {
    setRelatives((prev) => prev.map((r) => (r.patient_relative_id === updated.patient_relative_id ? updated : r)));
  }

  function handleUnlink(patientRelativeId: number) {
    setRelatives((prev) => prev.filter((r) => r.patient_relative_id !== patientRelativeId));
  }

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Familiares" />

      <div className="flex items-center justify-between rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div>
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Red familiar</h2>
          <Link href={`/residents/${id}`} className="text-xs text-brand-500 hover:underline">← Volver al perfil</Link>
        </div>
        <Button onClick={() => { setShowForm((v) => !v); setCreateError(null); }}>
          {showForm ? "Cancelar" : "Agregar familiar"}
        </Button>
      </div>

      {showForm && (
        <div className="rounded-2xl border border-brand-200 bg-white p-6 space-y-5 dark:border-brand-800/50 dark:bg-white/[0.03]">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">Nuevo familiar</h3>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <Field label="Parentesco *">
              <input type="text" value={form.relation_type} onChange={(e) => setField("relation_type", e.target.value)} placeholder="Ej. padre, madre, esposo/a..." className={inputCls} />
            </Field>
            <Field label="Nombre *">
              <input type="text" value={form.first_name} onChange={(e) => setField("first_name", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Apellido *">
              <input type="text" value={form.last_name} onChange={(e) => setField("last_name", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Cédula">
              <input type="text" value={form.id_number} onChange={(e) => setField("id_number", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Fecha de nacimiento">
              <input type="date" value={form.birthdate} onChange={(e) => setField("birthdate", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Estado civil">
              <select value={form.marital_status} onChange={(e) => setField("marital_status", e.target.value)} className={inputCls}>
                <option value="">— Seleccionar —</option>
                {Object.entries(MARITAL_STATUS_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </Field>
            <Field label="Teléfono">
              <input type="text" value={form.phone} onChange={(e) => setField("phone", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Escolaridad">
              <select value={form.education_level} onChange={(e) => setField("education_level", e.target.value)} className={inputCls}>
                <option value="">— Seleccionar —</option>
                {Object.entries(EDUCATION_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </Field>
            <Field label="Situación judicial">
              <input type="text" value={form.judicial_situation} onChange={(e) => setField("judicial_situation", e.target.value)} placeholder="Sin antecedentes, pendiente..." className={inputCls} />
            </Field>
            <div className="sm:col-span-2 lg:col-span-3">
              <Field label="Dirección">
                <input type="text" value={form.address} onChange={(e) => setField("address", e.target.value)} className={inputCls} />
              </Field>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {createError && <p role="alert" className="text-sm text-error-500">{createError}</p>}
            <Button onClick={handleCreate} disabled={creating} className="ml-auto">
              {creating ? "Agregando..." : "Agregar familiar"}
            </Button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {loading ? (
          <div className="p-6 text-sm text-gray-400">Cargando...</div>
        ) : relatives.length === 0 ? (
          <div className="rounded-2xl border border-gray-200 bg-white p-10 text-center text-sm text-gray-400 dark:border-gray-800 dark:bg-white/[0.03]">
            Sin familiares registrados.
          </div>
        ) : (
          relatives.map((r) => (
            <RelativeCard key={r.patient_relative_id} relative={r} onUpdate={handleUpdate} onUnlink={handleUnlink} />
          ))
        )}
      </div>
    </div>
  );
}
