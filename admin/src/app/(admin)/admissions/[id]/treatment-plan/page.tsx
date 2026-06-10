"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type { TreatmentPlanOut, TreatmentStageOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const STAGE_LABELS: Record<string, string> = {
  orientation: "Orientación",
  adaptation: "Adaptación",
  development: "Desarrollo",
  consolidation: "Consolidación",
  reintegration: "Reinserción social",
};

const STAGE_STATUSES = [
  { value: "pending", label: "Pendiente" },
  { value: "active", label: "En curso" },
  { value: "completed", label: "Completada" },
  { value: "extended", label: "Extendida" },
];

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  active: "bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-400",
  completed: "bg-success-50 text-success-700 dark:bg-success-900/30 dark:text-success-400",
  extended: "bg-warning-50 text-warning-700 dark:bg-warning-900/30 dark:text-warning-500",
};

type StageState = Omit<TreatmentStageOut, "id" | "stage_order">;

type FormState = {
  recommendations: string | null;
  plan_details: string | null;
  life_project: string | null;
  stages: StageState[];
};

function stageStateFromOut(s: TreatmentStageOut): StageState {
  return {
    stage_name: s.stage_name,
    start_date: s.start_date,
    end_date: s.end_date,
    progress_notes: s.progress_notes,
    extension_consent_signed: s.extension_consent_signed,
    advancement_criteria: s.advancement_criteria,
    status: s.status,
  };
}

function formFromOut(data: TreatmentPlanOut): FormState {
  return {
    recommendations: data.recommendations,
    plan_details: data.plan_details,
    life_project: data.life_project,
    stages: data.stages.map(stageStateFromOut),
  };
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>
      {children}
    </div>
  );
}

const inputCls =
  "w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white";

const sectionCls =
  "rounded-2xl border border-gray-200 bg-white p-6 space-y-5 dark:border-gray-800 dark:bg-white/[0.03]";

export default function TreatmentPlanPage() {
  const { id } = useParams<{ id: string }>();
  const [form, setForm] = useState<FormState>({
    recommendations: null,
    plan_details: null,
    life_project: null,
    stages: [],
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<TreatmentPlanOut>(`/admissions/${id}/treatment-plan`)
      .then((data) => setForm(formFromOut(data)))
      .finally(() => setLoading(false));
  }, [id]);

  function setField<K extends keyof Omit<FormState, "stages">>(
    field: K,
    value: FormState[K]
  ) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setSaved(false);
  }

  function updateStage(stageName: string, patch: Partial<StageState>) {
    setForm((prev) => ({
      ...prev,
      stages: prev.stages.map((s) =>
        s.stage_name === stageName ? { ...s, ...patch } : s
      ),
    }));
    setSaved(false);
  }

  async function handleSave() {
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      const updated = await apiFetch<TreatmentPlanOut>(
        `/admissions/${id}/treatment-plan`,
        { method: "PUT", body: JSON.stringify(form) }
      );
      setForm(formFromOut(updated));
      setSaved(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Plan de tratamiento" />

      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
          Plan de tratamiento
        </h2>
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
          {/* Plan general */}
          <div className={sectionCls}>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
              Plan general
            </h3>
            <Field label="Detalles del plan">
              <textarea
                rows={5}
                value={form.plan_details ?? ""}
                onChange={(e) => setField("plan_details", e.target.value || null)}
                placeholder="Descripción detallada del plan de tratamiento..."
                className={inputCls}
              />
            </Field>
            <Field label="Recomendaciones">
              <textarea
                rows={4}
                value={form.recommendations ?? ""}
                onChange={(e) => setField("recommendations", e.target.value || null)}
                placeholder="Recomendaciones del equipo terapéutico..."
                className={inputCls}
              />
            </Field>
            <Field label="Proyecto de vida">
              <textarea
                rows={4}
                value={form.life_project ?? ""}
                onChange={(e) => setField("life_project", e.target.value || null)}
                placeholder="Metas y proyecto de vida del paciente..."
                className={inputCls}
              />
            </Field>
          </div>

          {/* Etapas */}
          <div>
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-500">
              Etapas del programa
            </h3>
            <div className="space-y-4">
              {form.stages.map((stage, index) => (
                <div
                  key={stage.stage_name}
                  className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]"
                >
                  {/* Stage header */}
                  <div className="flex items-center justify-between mb-5">
                    <div className="flex items-center gap-3">
                      <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gray-100 text-xs font-bold text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                        {index + 1}
                      </span>
                      <h4 className="text-base font-semibold text-gray-800 dark:text-white">
                        {STAGE_LABELS[stage.stage_name] ?? stage.stage_name}
                      </h4>
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-medium ${
                        STATUS_COLORS[stage.status] ?? STATUS_COLORS.pending
                      }`}
                    >
                      {STAGE_STATUSES.find((s) => s.value === stage.status)?.label ?? stage.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                    <Field label="Estado">
                      <select
                        value={stage.status}
                        onChange={(e) =>
                          updateStage(stage.stage_name, { status: e.target.value })
                        }
                        className={inputCls}
                      >
                        {STAGE_STATUSES.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    </Field>
                    <Field label="Fecha de inicio">
                      <input
                        type="date"
                        value={stage.start_date ?? ""}
                        onChange={(e) =>
                          updateStage(stage.stage_name, {
                            start_date: e.target.value || null,
                          })
                        }
                        className={inputCls}
                      />
                    </Field>
                    <Field label="Fecha de fin">
                      <input
                        type="date"
                        value={stage.end_date ?? ""}
                        onChange={(e) =>
                          updateStage(stage.stage_name, {
                            end_date: e.target.value || null,
                          })
                        }
                        className={inputCls}
                      />
                    </Field>

                    <div className="sm:col-span-2 lg:col-span-3">
                      <Field label="Criterios de avance">
                        <textarea
                          rows={2}
                          value={stage.advancement_criteria ?? ""}
                          onChange={(e) =>
                            updateStage(stage.stage_name, {
                              advancement_criteria: e.target.value || null,
                            })
                          }
                          placeholder="Objetivos y criterios para avanzar a la siguiente etapa..."
                          className={inputCls}
                        />
                      </Field>
                    </div>

                    <div className="sm:col-span-2 lg:col-span-3">
                      <Field label="Notas de progreso">
                        <textarea
                          rows={3}
                          value={stage.progress_notes ?? ""}
                          onChange={(e) =>
                            updateStage(stage.stage_name, {
                              progress_notes: e.target.value || null,
                            })
                          }
                          placeholder="Observaciones sobre el progreso en esta etapa..."
                          className={inputCls}
                        />
                      </Field>
                    </div>

                    <div className="sm:col-span-2 lg:col-span-3">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={stage.extension_consent_signed}
                          onChange={(e) =>
                            updateStage(stage.stage_name, {
                              extension_consent_signed: e.target.checked,
                            })
                          }
                          className="h-4 w-4 accent-brand-500"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          Consentimiento de extensión firmado
                        </span>
                      </label>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              {error && (
                <p role="alert" className="text-sm text-error-500">
                  {error}
                </p>
              )}
              {saved && (
                <p className="text-sm text-success-600">Guardado correctamente.</p>
              )}
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
