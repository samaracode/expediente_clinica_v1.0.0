"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type { EconomicSituationOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const HOUSE_TYPES = [
  { value: "", label: "— Seleccionar —" },
  { value: "propia", label: "Propia" },
  { value: "alquilada", label: "Alquilada" },
  { value: "prestada", label: "Prestada" },
  { value: "otro", label: "Otro" },
];

type FormState = Omit<EconomicSituationOut, "id" | "admission_id">;

function emptyForm(): FormState {
  return {
    has_worked: null,
    current_job: null,
    work_phone: null,
    workplace: null,
    job_title: null,
    tenure_months: null,
    monthly_income_colones: null,
    house_type: null,
    rent_amount: null,
    family_income_notes: null,
    financial_assistance_notes: null,
    household_members: [],
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

export default function EconomicSituationPage() {
  const { id } = useParams<{ id: string }>();
  const [form, setForm] = useState<FormState>(emptyForm());
  const [newMember, setNewMember] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<EconomicSituationOut>(`/admissions/${id}/economic-situation`)
      .then(({ id: _id, admission_id: _aid, ...rest }) => setForm(rest))
      .finally(() => setLoading(false));
  }, [id]);

  function set<K extends keyof FormState>(field: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setSaved(false);
  }

  function addMember() {
    const name = newMember.trim();
    if (!name) return;
    set("household_members", [...form.household_members, name]);
    setNewMember("");
  }

  function removeMember(index: number) {
    set("household_members", form.household_members.filter((_, i) => i !== index));
  }

  async function handleSave() {
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      const updated = await apiFetch<EconomicSituationOut>(
        `/admissions/${id}/economic-situation`,
        { method: "PUT", body: JSON.stringify(form) }
      );
      const { id: _id, admission_id: _aid, ...rest } = updated;
      setForm(rest);
      setSaved(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  }

  const sectionCls = "rounded-2xl border border-gray-200 bg-white p-6 space-y-5 dark:border-gray-800 dark:bg-white/[0.03]";

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Situación económica" />

      {/* Header */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
          Situación económica y social
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
          {/* Situación laboral */}
          <div className={sectionCls}>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
              Situación laboral
            </h3>

            <Field label="¿Ha trabajado?">
              <div className="flex gap-6 mt-1">
                {[
                  { value: true, label: "Sí" },
                  { value: false, label: "No" },
                ].map((opt) => (
                  <label key={String(opt.value)} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
                    <input
                      type="radio"
                      name="has_worked"
                      checked={form.has_worked === opt.value}
                      onChange={() => set("has_worked", opt.value)}
                      className="accent-brand-500"
                    />
                    {opt.label}
                  </label>
                ))}
              </div>
            </Field>

            {form.has_worked && (
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                <Field label="Trabajo actual">
                  <input
                    type="text"
                    value={form.current_job ?? ""}
                    onChange={(e) => set("current_job", e.target.value || null)}
                    placeholder="Descripción del trabajo"
                    className={inputCls}
                  />
                </Field>
                <Field label="Lugar de trabajo">
                  <input
                    type="text"
                    value={form.workplace ?? ""}
                    onChange={(e) => set("workplace", e.target.value || null)}
                    placeholder="Nombre del empleador"
                    className={inputCls}
                  />
                </Field>
                <Field label="Cargo">
                  <input
                    type="text"
                    value={form.job_title ?? ""}
                    onChange={(e) => set("job_title", e.target.value || null)}
                    placeholder="Cargo o puesto"
                    className={inputCls}
                  />
                </Field>
                <Field label="Teléfono del trabajo">
                  <input
                    type="tel"
                    value={form.work_phone ?? ""}
                    onChange={(e) => set("work_phone", e.target.value || null)}
                    placeholder="2222-2222"
                    className={inputCls}
                  />
                </Field>
                <Field label="Antigüedad (meses)">
                  <input
                    type="number"
                    min={0}
                    value={form.tenure_months ?? ""}
                    onChange={(e) => set("tenure_months", e.target.value ? parseInt(e.target.value) : null)}
                    className={inputCls}
                  />
                </Field>
                <Field label="Ingreso mensual (₡)">
                  <input
                    type="number"
                    min={0}
                    step={1000}
                    value={form.monthly_income_colones ?? ""}
                    onChange={(e) => set("monthly_income_colones", e.target.value ? parseFloat(e.target.value) : null)}
                    placeholder="0"
                    className={inputCls}
                  />
                </Field>
              </div>
            )}
          </div>

          {/* Vivienda */}
          <div className={sectionCls}>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
              Vivienda
            </h3>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <Field label="Tipo de vivienda">
                <select
                  value={form.house_type ?? ""}
                  onChange={(e) => set("house_type", e.target.value || null)}
                  className={inputCls}
                >
                  {HOUSE_TYPES.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </Field>
              {form.house_type === "alquilada" && (
                <Field label="Monto del alquiler (₡)">
                  <input
                    type="number"
                    min={0}
                    step={1000}
                    value={form.rent_amount ?? ""}
                    onChange={(e) => set("rent_amount", e.target.value ? parseFloat(e.target.value) : null)}
                    placeholder="0"
                    className={inputCls}
                  />
                </Field>
              )}
            </div>
          </div>

          {/* Ingresos y apoyo */}
          <div className={sectionCls}>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
              Ingresos y apoyo económico
            </h3>
            <Field label="Ingresos familiares">
              <textarea
                rows={2}
                value={form.family_income_notes ?? ""}
                onChange={(e) => set("family_income_notes", e.target.value || null)}
                placeholder="Descripción de ingresos del grupo familiar..."
                className={inputCls}
              />
            </Field>
            <Field label="Apoyo económico externo">
              <textarea
                rows={2}
                value={form.financial_assistance_notes ?? ""}
                onChange={(e) => set("financial_assistance_notes", e.target.value || null)}
                placeholder="Becas, subsidios, ayudas de terceros..."
                className={inputCls}
              />
            </Field>
          </div>

          {/* Convivientes */}
          <div className={sectionCls}>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">
              Personas con quienes convive
            </h3>

            {form.household_members.length > 0 && (
              <ul className="space-y-2">
                {form.household_members.map((name, index) => (
                  <li key={index} className="flex items-center justify-between rounded-lg border border-gray-100 bg-gray-50 px-4 py-2 dark:border-gray-800 dark:bg-gray-800/50">
                    <span className="text-sm text-gray-700 dark:text-white">{name}</span>
                    <button
                      type="button"
                      onClick={() => removeMember(index)}
                      className="text-gray-300 hover:text-error-500 transition-colors"
                      aria-label="Eliminar"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </li>
                ))}
              </ul>
            )}

            <div className="flex gap-2">
              <input
                type="text"
                value={newMember}
                onChange={(e) => setNewMember(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addMember())}
                placeholder="Nombre del conviviente"
                className={`${inputCls} flex-1`}
              />
              <Button type="button" variant="outline" size="sm" onClick={addMember}>
                Agregar
              </Button>
            </div>
          </div>

          {/* Acciones */}
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
