"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type { TherapeuticAssessmentOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const COMPLETION_STATUS = [
  { value: "pending", label: "Pendiente" },
  { value: "in_progress", label: "En progreso" },
  { value: "completed", label: "Completada" },
];

type FormState = Omit<TherapeuticAssessmentOut, "id" | "admission_id" | "assessor_id">;

function emptyForm(): FormState {
  return {
    assessment_date: null,
    initial_summary: null,
    clinical_history_summary: null,
    europal_si_notes: null,
    socrates_notes: null,
    urica_notes: null,
    afc_analysis_notes: null,
    relapse_prevention_interview: null,
    relapse_prevention_plan: null,
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

export default function TherapeuticPage() {
  const { id } = useParams<{ id: string }>();
  const [form, setForm] = useState<FormState>(emptyForm());
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<TherapeuticAssessmentOut>(`/admissions/${id}/therapeutic`)
      .then(({ id: _id, admission_id: _aid, assessor_id: _asid, ...rest }) => setForm(rest))
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
      const updated = await apiFetch<TherapeuticAssessmentOut>(
        `/admissions/${id}/therapeutic`,
        { method: "PUT", body: JSON.stringify(form) }
      );
      const { id: _id, admission_id: _aid, assessor_id: _asid, ...rest } = updated;
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
      <PageBreadcrumb pageTitle="Evaluación terapéutica" />

      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Evaluación terapéutica</h2>
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
          {/* General */}
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

          {/* Evaluación */}
          <div className={sectionCls}>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">Evaluación</h3>
            <Field label="Resumen inicial">
              <textarea
                rows={4}
                value={form.initial_summary ?? ""}
                onChange={(e) => set("initial_summary", e.target.value || null)}
                placeholder="Resumen inicial de la evaluación terapéutica..."
                className={inputCls}
              />
            </Field>
            <Field label="Resumen de historia clínica">
              <textarea
                rows={6}
                value={form.clinical_history_summary ?? ""}
                onChange={(e) => set("clinical_history_summary", e.target.value || null)}
                placeholder="Resumen relevante de la historia clínica..."
                className={inputCls}
              />
            </Field>
          </div>

          {/* Escalas */}
          <div className={sectionCls}>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
              Escalas aplicadas
            </h3>
            <Field label="EUROPAL-SI">
              <textarea
                rows={3}
                value={form.europal_si_notes ?? ""}
                onChange={(e) => set("europal_si_notes", e.target.value || null)}
                placeholder="Resultados e interpretación EUROPAL-SI..."
                className={inputCls}
              />
            </Field>
            <Field label="SOCRATES">
              <textarea
                rows={3}
                value={form.socrates_notes ?? ""}
                onChange={(e) => set("socrates_notes", e.target.value || null)}
                placeholder="Resultados e interpretación SOCRATES..."
                className={inputCls}
              />
            </Field>
            <Field label="URICA">
              <textarea
                rows={3}
                value={form.urica_notes ?? ""}
                onChange={(e) => set("urica_notes", e.target.value || null)}
                placeholder="Resultados e interpretación URICA..."
                className={inputCls}
              />
            </Field>
          </div>

          {/* AFC */}
          <div className={sectionCls}>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
              Análisis funcional de la conducta (AFC)
            </h3>
            <Field label="Análisis AFC">
              <textarea
                rows={6}
                value={form.afc_analysis_notes ?? ""}
                onChange={(e) => set("afc_analysis_notes", e.target.value || null)}
                placeholder="Análisis funcional de la conducta adictiva..."
                className={inputCls}
              />
            </Field>
          </div>

          {/* Prevención de recaídas */}
          <div className={sectionCls}>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
              Prevención de recaídas
            </h3>
            <Field label="Entrevista de prevención de recaídas">
              <textarea
                rows={5}
                value={form.relapse_prevention_interview ?? ""}
                onChange={(e) => set("relapse_prevention_interview", e.target.value || null)}
                placeholder="Resumen de la entrevista de prevención de recaídas..."
                className={inputCls}
              />
            </Field>
            <Field label="Plan de prevención de recaídas">
              <textarea
                rows={5}
                value={form.relapse_prevention_plan ?? ""}
                onChange={(e) => set("relapse_prevention_plan", e.target.value || null)}
                placeholder="Estrategias y plan acordado para prevención de recaídas..."
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
