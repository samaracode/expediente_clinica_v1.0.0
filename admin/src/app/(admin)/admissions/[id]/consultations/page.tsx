"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type { ConsultationOut, TreatmentAreaOut, ProfessionalOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const AREA_LABELS: Record<string, string> = {
  medicine: "Medicina",
  therapeutic: "Terapéutica",
  social_work: "Trabajo Social",
  psychology: "Psicología",
  occupational_therapy: "T. Ocupacional",
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

type NewForm = {
  consultation_date: string;
  professional_id: string;
  area_id: string;
  consultation_type: string;
  description: string;
  observations: string;
  next_appointment_date: string;
};

const EMPTY_FORM: NewForm = {
  consultation_date: new Date().toISOString().slice(0, 10),
  professional_id: "",
  area_id: "",
  consultation_type: "",
  description: "",
  observations: "",
  next_appointment_date: "",
};

function EditableRow({
  consultation,
  areas,
  professionals,
  onUpdate,
  onDelete,
}: {
  consultation: ConsultationOut;
  areas: TreatmentAreaOut[];
  professionals: ProfessionalOut[];
  onUpdate: (c: ConsultationOut) => void;
  onDelete: (id: number) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [form, setForm] = useState<NewForm>({
    consultation_date: consultation.consultation_date,
    professional_id: String(consultation.professional_id ?? ""),
    area_id: String(consultation.area_id ?? ""),
    consultation_type: consultation.consultation_type ?? "",
    description: consultation.description ?? "",
    observations: consultation.observations ?? "",
    next_appointment_date: consultation.next_appointment_date ?? "",
  });
  const [saving, setSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  async function handleDelete(e: React.MouseEvent) {
    e.stopPropagation();
    setDeleting(true);
    try {
      await apiFetch(`/admissions/consultations/${consultation.id}`, { method: "DELETE" });
      onDelete(consultation.id);
    } finally {
      setDeleting(false);
    }
  }

  function setField<K extends keyof NewForm>(k: K, v: string) {
    setForm((prev) => ({ ...prev, [k]: v }));
  }

  async function save() {
    setSaving(true);
    try {
      const updated = await apiFetch<ConsultationOut>(`/admissions/consultations/${consultation.id}`, {
        method: "PUT",
        body: JSON.stringify({
          consultation_date: form.consultation_date || undefined,
          professional_id: form.professional_id ? parseInt(form.professional_id) : undefined,
          area_id: form.area_id ? parseInt(form.area_id) : undefined,
          consultation_type: form.consultation_type || undefined,
          description: form.description || undefined,
          observations: form.observations || undefined,
          next_appointment_date: form.next_appointment_date || undefined,
        }),
      });
      onUpdate(updated);
      setExpanded(false);
    } finally {
      setSaving(false);
    }
  }

  const areaLabel = consultation.area_name
    ? (AREA_LABELS[consultation.area_name] ?? consultation.area_name)
    : "—";

  return (
    <>
      <tr
        className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-white/[0.02] cursor-pointer"
        onClick={() => setExpanded((v) => !v)}
      >
        <td className="px-4 py-3 text-sm text-gray-700 dark:text-white">
          {new Date(consultation.consultation_date + "T12:00:00").toLocaleDateString("es-CR")}
        </td>
        <td className="px-4 py-3 text-sm text-gray-700 dark:text-white">
          {consultation.professional_name ?? "—"}
        </td>
        <td className="px-4 py-3">
          {consultation.area_name && (
            <span className="rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-medium text-brand-700 dark:bg-brand-900/20 dark:text-brand-400">
              {areaLabel}
            </span>
          )}
        </td>
        <td className="px-4 py-3 text-sm text-gray-500">{consultation.consultation_type ?? "—"}</td>
        <td className="px-4 py-3 text-xs text-gray-400">
          {consultation.next_appointment_date
            ? new Date(consultation.next_appointment_date + "T12:00:00").toLocaleDateString("es-CR")
            : "—"}
        </td>
        <td className="px-4 py-3 text-right" onClick={(e) => e.stopPropagation()}>
          {confirmDelete ? (
            <span className="flex items-center justify-end gap-1">
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="rounded px-2 py-0.5 text-xs font-medium bg-error-500 text-white hover:bg-error-600 disabled:opacity-50"
              >
                {deleting ? "..." : "Sí"}
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); setConfirmDelete(false); }}
                className="rounded px-2 py-0.5 text-xs border border-gray-300 text-gray-500"
              >
                No
              </button>
            </span>
          ) : (
            <span className="flex items-center justify-end gap-3">
              <button
                onClick={(e) => { e.stopPropagation(); setConfirmDelete(true); }}
                className="text-xs text-error-500 hover:underline"
              >
                Eliminar
              </button>
              <span className="text-xs text-brand-500">{expanded ? "▲" : "▼"}</span>
            </span>
          )}
        </td>
      </tr>
      {expanded && (
        <tr className="border-b border-brand-100 dark:border-brand-800/30 bg-brand-50/30 dark:bg-brand-900/5">
          <td colSpan={6} className="px-4 py-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <Field label="Fecha">
                <input type="date" value={form.consultation_date} onChange={(e) => setField("consultation_date", e.target.value)} className={inputCls} />
              </Field>
              <Field label="Profesional">
                <select value={form.professional_id} onChange={(e) => setField("professional_id", e.target.value)} className={inputCls}>
                  <option value="">— Sin asignar —</option>
                  {professionals.map((p) => (
                    <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
                  ))}
                </select>
              </Field>
              <Field label="Área">
                <select value={form.area_id} onChange={(e) => setField("area_id", e.target.value)} className={inputCls}>
                  <option value="">— Sin asignar —</option>
                  {areas.map((a) => (
                    <option key={a.id} value={a.id}>{AREA_LABELS[a.name] ?? a.name}</option>
                  ))}
                </select>
              </Field>
              <Field label="Tipo de consulta">
                <input type="text" value={form.consultation_type} onChange={(e) => setField("consultation_type", e.target.value)} placeholder="Ej. seguimiento, emergencia..." className={inputCls} />
              </Field>
              <Field label="Próxima cita">
                <input type="date" value={form.next_appointment_date} onChange={(e) => setField("next_appointment_date", e.target.value)} className={inputCls} />
              </Field>
              <div className="sm:col-span-2 lg:col-span-3">
                <Field label="Descripción / Motivo">
                  <textarea rows={2} value={form.description} onChange={(e) => setField("description", e.target.value)} className={inputCls} />
                </Field>
              </div>
              <div className="sm:col-span-2 lg:col-span-3">
                <Field label="Observaciones">
                  <textarea rows={2} value={form.observations} onChange={(e) => setField("observations", e.target.value)} className={inputCls} />
                </Field>
              </div>
            </div>
            <div className="mt-3 flex justify-end gap-3">
              <button type="button" onClick={() => setExpanded(false)} className="text-sm text-gray-400 hover:text-gray-600">
                Cancelar
              </button>
              <Button onClick={save} disabled={saving}>
                {saving ? "Guardando..." : "Guardar cambios"}
              </Button>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

export default function ConsultationsPage() {
  const { id } = useParams<{ id: string }>();
  const [consultations, setConsultations] = useState<ConsultationOut[]>([]);
  const [areas, setAreas] = useState<TreatmentAreaOut[]>([]);
  const [professionals, setProfessionals] = useState<ProfessionalOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<NewForm>(EMPTY_FORM);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [areaFilter, setAreaFilter] = useState("");

  // Load areas and professionals once
  useEffect(() => {
    Promise.all([
      apiFetch<TreatmentAreaOut[]>("/professionals/areas"),
      apiFetch<ProfessionalOut[]>("/professionals/"),
    ]).then(([a, p]) => {
      setAreas(a);
      setProfessionals(p.filter((pr) => pr.is_active));
    });
  }, []);

  // Reload consultations when area filter changes
  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (areaFilter) params.set("area_id", areaFilter);
    const qs = params.toString() ? `?${params}` : "";
    apiFetch<ConsultationOut[]>(`/admissions/${id}/consultations${qs}`)
      .then(setConsultations)
      .finally(() => setLoading(false));
  }, [id, areaFilter]);

  function setField<K extends keyof NewForm>(k: K, v: string) {
    setForm((prev) => ({ ...prev, [k]: v }));
  }

  async function handleCreate() {
    if (!form.consultation_date) {
      setCreateError("La fecha de consulta es obligatoria.");
      return;
    }
    setCreating(true);
    setCreateError(null);
    try {
      const created = await apiFetch<ConsultationOut>(`/admissions/${id}/consultations`, {
        method: "POST",
        body: JSON.stringify({
          consultation_date: form.consultation_date,
          professional_id: form.professional_id ? parseInt(form.professional_id) : null,
          area_id: form.area_id ? parseInt(form.area_id) : null,
          consultation_type: form.consultation_type || null,
          description: form.description || null,
          observations: form.observations || null,
          next_appointment_date: form.next_appointment_date || null,
        }),
      });
      setConsultations((prev) => [created, ...prev]);
      setForm(EMPTY_FORM);
      setShowForm(false);
    } catch (err) {
      setCreateError(err instanceof ApiError ? err.message : "Error al crear consulta");
    } finally {
      setCreating(false);
    }
  }

  function handleUpdate(updated: ConsultationOut) {
    setConsultations((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
  }

  function handleDelete(consultationId: number) {
    setConsultations((prev) => prev.filter((c) => c.id !== consultationId));
  }

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Consultas de seguimiento" />

      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Consultas de seguimiento</h2>
            <Link href={`/admissions/${id}`} className="text-xs text-brand-500 hover:underline">← Volver al expediente</Link>
          </div>
          <div className="flex items-end gap-3">
            <div>
              <label className="mb-1 block text-xs text-gray-400">Filtrar por área</label>
              <select
                value={areaFilter}
                onChange={(e) => setAreaFilter(e.target.value)}
                className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
              >
                <option value="">Todas las áreas</option>
                {areas.map((a) => (
                  <option key={a.id} value={a.id}>{AREA_LABELS[a.name] ?? a.name}</option>
                ))}
              </select>
            </div>
            <Button onClick={() => { setShowForm((v) => !v); setCreateError(null); }}>
              {showForm ? "Cancelar" : "Nueva consulta"}
            </Button>
          </div>
        </div>
      </div>

      {showForm && (
        <div className="rounded-2xl border border-brand-200 bg-white p-6 space-y-5 dark:border-brand-800/50 dark:bg-white/[0.03]">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">Nueva consulta</h3>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <Field label="Fecha *">
              <input type="date" value={form.consultation_date} onChange={(e) => setField("consultation_date", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Profesional">
              <select value={form.professional_id} onChange={(e) => setField("professional_id", e.target.value)} className={inputCls}>
                <option value="">— Sin asignar —</option>
                {professionals.map((p) => (
                  <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
                ))}
              </select>
            </Field>
            <Field label="Área">
              <select value={form.area_id} onChange={(e) => setField("area_id", e.target.value)} className={inputCls}>
                <option value="">— Sin asignar —</option>
                {areas.map((a) => (
                  <option key={a.id} value={a.id}>{AREA_LABELS[a.name] ?? a.name}</option>
                ))}
              </select>
            </Field>
            <Field label="Tipo de consulta">
              <input type="text" value={form.consultation_type} onChange={(e) => setField("consultation_type", e.target.value)} placeholder="Ej. seguimiento, emergencia..." className={inputCls} />
            </Field>
            <Field label="Próxima cita">
              <input type="date" value={form.next_appointment_date} onChange={(e) => setField("next_appointment_date", e.target.value)} className={inputCls} />
            </Field>
            <div className="sm:col-span-2">
              <Field label="Descripción / Motivo">
                <textarea rows={2} value={form.description} onChange={(e) => setField("description", e.target.value)} className={inputCls} />
              </Field>
            </div>
            <div className="sm:col-span-2 lg:col-span-3">
              <Field label="Observaciones">
                <textarea rows={2} value={form.observations} onChange={(e) => setField("observations", e.target.value)} className={inputCls} />
              </Field>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {createError && <p role="alert" className="text-sm text-error-500">{createError}</p>}
            <Button onClick={handleCreate} disabled={creating} className="ml-auto">
              {creating ? "Creando..." : "Crear consulta"}
            </Button>
          </div>
        </div>
      )}

      <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] overflow-hidden">
        {loading ? (
          <div className="p-6 text-sm text-gray-400">Cargando...</div>
        ) : consultations.length === 0 ? (
          <div className="p-10 text-center text-sm text-gray-400">Sin consultas registradas para esta admisión.</div>
        ) : (
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50 dark:border-gray-800 dark:bg-white/[0.02]">
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Fecha</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Profesional</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Área</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Tipo</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Próxima cita</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {consultations.map((c) => (
                <EditableRow
                  key={c.id}
                  consultation={c}
                  areas={areas}
                  professionals={professionals}
                  onUpdate={handleUpdate}
                  onDelete={handleDelete}
                />
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
