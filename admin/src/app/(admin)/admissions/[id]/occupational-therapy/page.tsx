"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type { OccupationalTherapyAssessmentOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const COMPLETION_STATUS = [
  { value: "pending", label: "Pendiente" },
  { value: "in_progress", label: "En progreso" },
  { value: "completed", label: "Completada" },
];

type FormState = Omit<OccupationalTherapyAssessmentOut, "id" | "admission_id" | "therapist_id">;

function emptyForm(): FormState {
  return {
    assessment_date: null,
    initial_diagnostic_impression: null,
    occupational_profile: null,
    completion_status: "pending",
  };
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">{label}</label>
      {children}
    </div>
  );
}

const inputCls =
  "w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white";

const sectionCls =
  "rounded-2xl border border-gray-200 bg-white p-6 space-y-5 dark:border-gray-800 dark:bg-white/[0.03]";

export default function OccupationalTherapyPage() {
  const { id } = useParams<{ id: string }>();
  const [form, setForm] = useState<FormState>(emptyForm());
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<OccupationalTherapyAssessmentOut>(`/admissions/${id}/occupational-therapy`)
      .then(({ id: _id, admission_id: _aid, therapist_id: _tid, ...rest }) => setForm(rest))
      .finally(() => setLoading(false));
  }, [id]);

  function set<K extends keyof FormState>(field: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setSaved(false);
  }

  async function handleSave() {
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      const updated = await apiFetch<OccupationalTherapyAssessmentOut>(
        `/admissions/${id}/occupational-therapy`,
        { method: "PUT", body: JSON.stringify(form) }
      );
      const { id: _id, admission_id: _aid, therapist_id: _tid, ...rest } = updated;
      setForm(rest);
      setSaved(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Terapia ocupacional" />

      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Evaluación de terapia ocupacional</h2>
        <p className="text-sm text-gray-500">
          <Link href={`/admissions/${id}`} className="text-brand-500 hover:underline">
            Admisión #{id}
          </Link>
        </p>
      </div>

      {loading ? (
        <div className="text-sm text-gray-400">Cargando...</div>
      ) : (
        <>
          <div className={sectionCls}>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">General</h3>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <Field label="Fecha de evaluación">
                <input
                  type="date"
                  value={form.assessment_date ?? ""}
                  onChange={(e) => set("assessment_date", e.target.value || null)}
                  className={inputCls}
                />
              </Field>
              <Field label="Estado">
                <select
                  value={form.completion_status}
                  onChange={(e) => set("completion_status", e.target.value)}
                  className={inputCls}
                >
                  {COMPLETION_STATUS.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </Field>
            </div>
          </div>

          <div className={sectionCls}>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
              Perfil ocupacional
            </h3>
            <Field label="Impresión diagnóstica inicial">
              <textarea
                rows={4}
                value={form.initial_diagnostic_impression ?? ""}
                onChange={(e) => set("initial_diagnostic_impression", e.target.value || null)}
                placeholder="Impresión diagnóstica desde perspectiva ocupacional..."
                className={inputCls}
              />
            </Field>
            <Field label="Perfil ocupacional">
              <textarea
                rows={8}
                value={form.occupational_profile ?? ""}
                onChange={(e) => set("occupational_profile", e.target.value || null)}
                placeholder="Descripción del perfil ocupacional: rutinas, roles, intereses, contextos..."
                className={inputCls}
              />
            </Field>
          </div>

          <div className="flex items-center justify-between">
            <div>
              {error && <p role="alert" className="text-sm text-error-500">{error}</p>}
              {saved && <p className="text-sm text-success-600">Guardado correctamente.</p>}
            </div>
            <Button onClick={handleSave} disabled={saving}>
              {saving ? "Guardando..." : "Guardar"}
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
