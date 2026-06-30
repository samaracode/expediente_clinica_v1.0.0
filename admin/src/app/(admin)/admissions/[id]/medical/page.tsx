"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type { DrugTestItem, MedicationLogItem, MedicalRecordOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const COMPLETION_STATUS = [
  { value: "pending", label: "Pendiente" },
  { value: "in_progress", label: "En progreso" },
  { value: "completed", label: "Completada" },
];

const DRUG_RESULTS = [
  { value: "", label: "— Resultado —" },
  { value: "negative", label: "Negativo" },
  { value: "positive", label: "Positivo" },
  { value: "pending", label: "Pendiente" },
];

const TREATMENT_TYPES = [
  { value: "", label: "— Tipo —" },
  { value: "internal", label: "Interno" },
  { value: "external", label: "Externo" },
];

type FormState = {
  social_security_validated: boolean;
  iafa_icd_notes: string | null;
  completion_status: string;
  drug_tests: DrugTestItem[];
  medication_logs: MedicationLogItem[];
};

function emptyForm(): FormState {
  return {
    social_security_validated: false,
    iafa_icd_notes: null,
    completion_status: "pending",
    drug_tests: [],
    medication_logs: [],
  };
}

function emptyDrugTest(): DrugTestItem {
  return { id: null, test_date: "", result: null, notes: null };
}

function emptyMedication(): MedicationLogItem {
  return {
    id: null,
    treatment_type: null,
    medication_name: "",
    dosage: null,
    frequency: null,
    prescribed_by: null,
    start_date: null,
    end_date: null,
    notes: null,
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

export default function MedicalPage() {
  const { id } = useParams<{ id: string }>();
  const [form, setForm] = useState<FormState>(emptyForm());
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<MedicalRecordOut>(`/admissions/${id}/medical`).then((data) => {
      setForm({
        social_security_validated: data.social_security_validated,
        iafa_icd_notes: data.iafa_icd_notes,
        completion_status: data.completion_status,
        drug_tests: data.drug_tests,
        medication_logs: data.medication_logs,
      });
    }).finally(() => setLoading(false));
  }, [id]);

  function setField<K extends keyof FormState>(field: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setSaved(false);
  }

  function updateDrugTest(index: number, patch: Partial<DrugTestItem>) {
    setForm((prev) => ({
      ...prev,
      drug_tests: prev.drug_tests.map((t, i) => (i === index ? { ...t, ...patch } : t)),
    }));
    setSaved(false);
  }

  function removeDrugTest(index: number) {
    setForm((prev) => ({
      ...prev,
      drug_tests: prev.drug_tests.filter((_, i) => i !== index),
    }));
    setSaved(false);
  }

  function updateMedication(index: number, patch: Partial<MedicationLogItem>) {
    setForm((prev) => ({
      ...prev,
      medication_logs: prev.medication_logs.map((m, i) => (i === index ? { ...m, ...patch } : m)),
    }));
    setSaved(false);
  }

  function removeMedication(index: number) {
    setForm((prev) => ({
      ...prev,
      medication_logs: prev.medication_logs.filter((_, i) => i !== index),
    }));
    setSaved(false);
  }

  async function handleSave() {
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      const updated = await apiFetch<MedicalRecordOut>(
        `/admissions/${id}/medical`,
        { method: "PUT", body: JSON.stringify(form) }
      );
      setForm({
        social_security_validated: updated.social_security_validated,
        iafa_icd_notes: updated.iafa_icd_notes,
        completion_status: updated.completion_status,
        drug_tests: updated.drug_tests,
        medication_logs: updated.medication_logs,
      });
      setSaved(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Evaluación médica" />

      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Evaluación médica</h2>
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
              <Field label="Estado">
                <select
                  value={form.completion_status}
                  onChange={(e) => setField("completion_status", e.target.value)}
                  className={inputCls}
                >
                  {COMPLETION_STATUS.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </Field>
              <Field label="Seguro Social">
                <label className="flex items-center gap-2 mt-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.social_security_validated}
                    onChange={(e) => setField("social_security_validated", e.target.checked)}
                    className="h-4 w-4 accent-brand-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Seguro Social validado
                  </span>
                </label>
              </Field>
            </div>
            <Field label="Notas IAFA / CIE">
              <textarea
                rows={3}
                value={form.iafa_icd_notes ?? ""}
                onChange={(e) => setField("iafa_icd_notes", e.target.value || null)}
                placeholder="Diagnósticos CIE, datos IAFA, observaciones médicas generales..."
                className={inputCls}
              />
            </Field>
          </div>

          {/* Pruebas de droga */}
          <div className={sectionCls}>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
                Pruebas de droga
              </h3>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setField("drug_tests", [...form.drug_tests, emptyDrugTest()])}
              >
                + Agregar prueba
              </Button>
            </div>

            {form.drug_tests.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">Sin pruebas registradas</p>
            ) : (
              <div className="space-y-3">
                {form.drug_tests.map((test, index) => (
                  <div
                    key={index}
                    className="grid grid-cols-1 gap-3 rounded-xl border border-gray-100 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-800/30 sm:grid-cols-3"
                  >
                    <Field label="Fecha">
                      <input
                        type="date"
                        value={test.test_date}
                        onChange={(e) => updateDrugTest(index, { test_date: e.target.value })}
                        className={inputCls}
                      />
                    </Field>
                    <Field label="Resultado">
                      <select
                        value={test.result ?? ""}
                        onChange={(e) => updateDrugTest(index, { result: e.target.value || null })}
                        className={inputCls}
                      >
                        {DRUG_RESULTS.map((opt) => (
                          <option key={opt.value} value={opt.value}>{opt.label}</option>
                        ))}
                      </select>
                    </Field>
                    <div className="flex gap-2 items-end">
                      <Field label="Notas">
                        <input
                          type="text"
                          value={test.notes ?? ""}
                          onChange={(e) => updateDrugTest(index, { notes: e.target.value || null })}
                          placeholder="Observaciones..."
                          className={inputCls}
                        />
                      </Field>
                      <button
                        type="button"
                        onClick={() => removeDrugTest(index)}
                        className="mb-0.5 text-gray-300 hover:text-error-500 transition-colors flex-shrink-0"
                        aria-label="Eliminar prueba"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Medicamentos */}
          <div className={sectionCls}>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
                Medicamentos
              </h3>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setField("medication_logs", [...form.medication_logs, emptyMedication()])}
              >
                + Agregar medicamento
              </Button>
            </div>

            {form.medication_logs.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">Sin medicamentos registrados</p>
            ) : (
              <div className="space-y-4">
                {form.medication_logs.map((med, index) => (
                  <div
                    key={index}
                    className="rounded-xl border border-gray-100 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-800/30"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                        Medicamento {index + 1}
                      </span>
                      <button
                        type="button"
                        onClick={() => removeMedication(index)}
                        className="text-gray-300 hover:text-error-500 transition-colors"
                        aria-label="Eliminar medicamento"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                      <Field label="Nombre del medicamento *">
                        <input
                          type="text"
                          value={med.medication_name}
                          onChange={(e) => updateMedication(index, { medication_name: e.target.value })}
                          placeholder="Nombre del medicamento"
                          className={inputCls}
                        />
                      </Field>
                      <Field label="Dosis">
                        <input
                          type="text"
                          value={med.dosage ?? ""}
                          onChange={(e) => updateMedication(index, { dosage: e.target.value || null })}
                          placeholder="ej. 10mg"
                          className={inputCls}
                        />
                      </Field>
                      <Field label="Frecuencia">
                        <input
                          type="text"
                          value={med.frequency ?? ""}
                          onChange={(e) => updateMedication(index, { frequency: e.target.value || null })}
                          placeholder="ej. cada 8 horas"
                          className={inputCls}
                        />
                      </Field>
                      <Field label="Prescrito por">
                        <input
                          type="text"
                          value={med.prescribed_by ?? ""}
                          onChange={(e) => updateMedication(index, { prescribed_by: e.target.value || null })}
                          placeholder="Nombre del médico"
                          className={inputCls}
                        />
                      </Field>
                      <Field label="Tipo de tratamiento">
                        <select
                          value={med.treatment_type ?? ""}
                          onChange={(e) => updateMedication(index, { treatment_type: e.target.value || null })}
                          className={inputCls}
                        >
                          {TREATMENT_TYPES.map((opt) => (
                            <option key={opt.value} value={opt.value}>{opt.label}</option>
                          ))}
                        </select>
                      </Field>
                      <div className="grid grid-cols-2 gap-2">
                        <Field label="Fecha inicio">
                          <input
                            type="date"
                            value={med.start_date ?? ""}
                            onChange={(e) => updateMedication(index, { start_date: e.target.value || null })}
                            className={inputCls}
                          />
                        </Field>
                        <Field label="Fecha fin">
                          <input
                            type="date"
                            value={med.end_date ?? ""}
                            onChange={(e) => updateMedication(index, { end_date: e.target.value || null })}
                            className={inputCls}
                          />
                        </Field>
                      </div>
                      <div className="sm:col-span-2 lg:col-span-3">
                        <Field label="Notas">
                          <input
                            type="text"
                            value={med.notes ?? ""}
                            onChange={(e) => updateMedication(index, { notes: e.target.value || null })}
                            placeholder="Observaciones adicionales..."
                            className={inputCls}
                          />
                        </Field>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
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
