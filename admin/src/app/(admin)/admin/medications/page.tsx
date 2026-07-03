"use client";

import { useEffect, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import type { MedicationOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

type NewMedForm = {
  name: string;
  form: string;
  strength: string;
  is_controlled: boolean;
  notes: string;
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

function MedRow({ med, onUpdate }: { med: MedicationOut; onUpdate: (m: MedicationOut) => void }) {
  const [name, setName] = useState(med.name);
  const [form, setForm] = useState(med.form ?? "");
  const [strength, setStrength] = useState(med.strength ?? "");
  const [saving, setSaving] = useState(false);

  const dirty =
    name !== med.name || form !== (med.form ?? "") || strength !== (med.strength ?? "");

  async function save() {
    setSaving(true);
    try {
      const updated = await apiFetch<MedicationOut>(`/medications/${med.id}`, {
        method: "PUT",
        body: JSON.stringify({ name, form: form || null, strength: strength || null }),
      });
      onUpdate(updated);
    } finally {
      setSaving(false);
    }
  }

  async function toggleControlled() {
    setSaving(true);
    try {
      const updated = await apiFetch<MedicationOut>(`/medications/${med.id}`, {
        method: "PUT",
        body: JSON.stringify({ is_controlled: !med.is_controlled }),
      });
      onUpdate(updated);
    } finally {
      setSaving(false);
    }
  }

  return (
    <tr className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-white/[0.02]">
      <td className="px-4 py-3">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="rounded-lg border border-gray-200 bg-white px-2 py-1 text-xs text-gray-700 focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white w-40"
        />
      </td>
      <td className="px-4 py-3">
        <input
          type="text"
          value={form}
          onChange={(e) => setForm(e.target.value)}
          placeholder="Forma"
          className="rounded-lg border border-gray-200 bg-white px-2 py-1 text-xs text-gray-700 focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white w-28"
        />
      </td>
      <td className="px-4 py-3">
        <input
          type="text"
          value={strength}
          onChange={(e) => setStrength(e.target.value)}
          placeholder="Concentración"
          className="rounded-lg border border-gray-200 bg-white px-2 py-1 text-xs text-gray-700 focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white w-28"
        />
      </td>
      <td className="px-4 py-3">
        <button
          type="button"
          onClick={toggleControlled}
          disabled={saving}
          className={`rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors ${
            med.is_controlled
              ? "bg-warning-50 text-warning-700 hover:bg-warning-100 dark:bg-warning-900/20 dark:text-warning-400"
              : "bg-gray-100 text-gray-500 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400"
          }`}
        >
          {med.is_controlled ? "Controlado" : "No controlado"}
        </button>
      </td>
      <td className="px-4 py-3">
        {dirty && (
          <button type="button" onClick={save} disabled={saving} className="text-xs text-brand-500 hover:underline">
            Guardar
          </button>
        )}
      </td>
    </tr>
  );
}

export default function MedicationsPage() {
  const [medications, setMedications] = useState<MedicationOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<NewMedForm>({
    name: "",
    form: "",
    strength: "",
    is_controlled: false,
    notes: "",
  });
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<MedicationOut[]>("/medications").then(setMedications).finally(() => setLoading(false));
  }, []);

  function setField<K extends keyof NewMedForm>(k: K, v: NewMedForm[K]) {
    setForm((prev) => ({ ...prev, [k]: v }));
  }

  async function handleCreate() {
    if (!form.name) {
      setCreateError("El nombre es obligatorio.");
      return;
    }
    setCreating(true);
    setCreateError(null);
    try {
      const created = await apiFetch<MedicationOut>("/medications", {
        method: "POST",
        body: JSON.stringify({
          name: form.name,
          form: form.form || undefined,
          strength: form.strength || undefined,
          is_controlled: form.is_controlled,
          notes: form.notes || undefined,
        }),
      });
      setMedications((prev) => [...prev, created].sort((a, b) => a.name.localeCompare(b.name)));
      setForm({ name: "", form: "", strength: "", is_controlled: false, notes: "" });
      setShowForm(false);
    } catch (err) {
      setCreateError(err instanceof ApiError ? err.message : "Error al crear");
    } finally {
      setCreating(false);
    }
  }

  function handleUpdate(updated: MedicationOut) {
    setMedications((prev) => prev.map((m) => (m.id === updated.id ? updated : m)));
  }

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Medicamentos" />

      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
            Catálogo de medicamentos
          </h2>
          <Button onClick={() => { setShowForm((v) => !v); setCreateError(null); }}>
            {showForm ? "Cancelar" : "Nuevo medicamento"}
          </Button>
        </div>
        <p className="mt-2 text-sm text-gray-400">
          El personal solo elige de esta lista al prescribir. Para agregar un fármaco nuevo,
          hacelo aquí primero.
        </p>
      </div>

      {showForm && (
        <div className="rounded-2xl border border-brand-200 bg-white p-6 space-y-5 dark:border-brand-800/50 dark:bg-white/[0.03]">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">Nuevo medicamento</h3>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <Field label="Nombre *">
              <input type="text" value={form.name} onChange={(e) => setField("name", e.target.value)} placeholder="Nombre" className={inputCls} />
            </Field>
            <Field label="Forma">
              <input type="text" value={form.form} onChange={(e) => setField("form", e.target.value)} placeholder="Tableta, jarabe, etc." className={inputCls} />
            </Field>
            <Field label="Concentración">
              <input type="text" value={form.strength} onChange={(e) => setField("strength", e.target.value)} placeholder="5 mg" className={inputCls} />
            </Field>
            <Field label="Notas">
              <input type="text" value={form.notes} onChange={(e) => setField("notes", e.target.value)} placeholder="Notas" className={inputCls} />
            </Field>
            <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 sm:col-span-2 lg:col-span-1">
              <input
                type="checkbox"
                checked={form.is_controlled}
                onChange={(e) => setField("is_controlled", e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
              />
              Medicamento controlado
            </label>
          </div>
          <div className="flex items-center gap-4">
            {createError && <p role="alert" className="text-sm text-error-500">{createError}</p>}
            <Button onClick={handleCreate} disabled={creating} className="ml-auto">
              {creating ? "Creando..." : "Crear medicamento"}
            </Button>
          </div>
        </div>
      )}

      <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] overflow-hidden">
        {loading ? (
          <div className="p-6 text-sm text-gray-400">Cargando...</div>
        ) : medications.length === 0 ? (
          <div className="p-10 text-center text-sm text-gray-400">Sin medicamentos registrados.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-white/[0.02]">
                  <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Nombre</th>
                  <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Forma</th>
                  <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Concentración</th>
                  <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Control</th>
                  <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500"></th>
                </tr>
              </thead>
              <tbody>
                {medications.map((m) => (
                  <MedRow key={m.id} med={m} onUpdate={handleUpdate} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
