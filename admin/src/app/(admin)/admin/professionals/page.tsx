"use client";

import { useEffect, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import type { ProfessionalOut, TreatmentAreaOut, UserAdminOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const AREA_LABELS: Record<string, string> = {
  medicine: "Medicina",
  therapeutic: "Terapéutica",
  social_work: "Trabajo Social",
  psychology: "Psicología",
  occupational_therapy: "Terapia Ocupacional",
};

type NewProfForm = {
  user_id: string;
  area_id: string;
  first_name: string;
  last_name: string;
  specialty: string;
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

function ProfRow({
  prof,
  areas,
  onUpdate,
}: {
  prof: ProfessionalOut;
  areas: TreatmentAreaOut[];
  onUpdate: (p: ProfessionalOut) => void;
}) {
  const [specialty, setSpecialty] = useState(prof.specialty ?? "");
  const [saving, setSaving] = useState(false);

  const areaLabel = AREA_LABELS[prof.area_name ?? ""] ?? prof.area_name ?? "—";

  async function saveSpecialty() {
    setSaving(true);
    try {
      const updated = await apiFetch<ProfessionalOut>(`/professionals/${prof.id}`, {
        method: "PUT",
        body: JSON.stringify({ specialty: specialty || null }),
      });
      onUpdate(updated);
    } finally {
      setSaving(false);
    }
  }

  async function toggleActive() {
    setSaving(true);
    try {
      const updated = await apiFetch<ProfessionalOut>(`/professionals/${prof.id}`, {
        method: "PUT",
        body: JSON.stringify({ is_active: !prof.is_active }),
      });
      onUpdate(updated);
    } finally {
      setSaving(false);
    }
  }

  return (
    <tr className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-white/[0.02]">
      <td className="px-4 py-3">
        <p className="text-sm font-medium text-gray-800 dark:text-white">
          {prof.first_name} {prof.last_name}
        </p>
        <p className="text-xs text-gray-400">{prof.user_email ?? "—"}</p>
      </td>
      <td className="px-4 py-3">
        <span className="rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-medium text-brand-700 dark:bg-brand-900/20 dark:text-brand-400">
          {areaLabel}
        </span>
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={specialty}
            onChange={(e) => setSpecialty(e.target.value)}
            placeholder="Especialidad"
            className="rounded-lg border border-gray-200 bg-white px-2 py-1 text-xs text-gray-700 focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white w-40"
          />
          {specialty !== (prof.specialty ?? "") && (
            <button type="button" onClick={saveSpecialty} disabled={saving} className="text-xs text-brand-500 hover:underline">
              Guardar
            </button>
          )}
        </div>
      </td>
      <td className="px-4 py-3">
        <button
          type="button"
          onClick={toggleActive}
          disabled={saving}
          className={`rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors ${
            prof.is_active
              ? "bg-success-50 text-success-700 hover:bg-success-100 dark:bg-success-900/20 dark:text-success-400"
              : "bg-gray-100 text-gray-500 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400"
          }`}
        >
          {prof.is_active ? "Activo" : "Inactivo"}
        </button>
      </td>
    </tr>
  );
}

export default function ProfessionalsPage() {
  const [professionals, setProfessionals] = useState<ProfessionalOut[]>([]);
  const [areas, setAreas] = useState<TreatmentAreaOut[]>([]);
  const [users, setUsers] = useState<UserAdminOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<NewProfForm>({ user_id: "", area_id: "", first_name: "", last_name: "", specialty: "" });
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiFetch<ProfessionalOut[]>("/professionals/"),
      apiFetch<TreatmentAreaOut[]>("/professionals/areas"),
      apiFetch<UserAdminOut[]>("/users/"),
    ]).then(([profs, areasData, usersData]) => {
      setProfessionals(profs);
      setAreas(areasData);
      setUsers(usersData);
    }).finally(() => setLoading(false));
  }, []);

  function setField<K extends keyof NewProfForm>(k: K, v: string) {
    setForm((prev) => ({ ...prev, [k]: v }));
  }

  async function handleCreate() {
    if (!form.user_id || !form.area_id || !form.first_name || !form.last_name) {
      setCreateError("Usuario, área, nombre y apellido son obligatorios.");
      return;
    }
    setCreating(true);
    setCreateError(null);
    try {
      const created = await apiFetch<ProfessionalOut>("/professionals/", {
        method: "POST",
        body: JSON.stringify({
          user_id: parseInt(form.user_id),
          area_id: parseInt(form.area_id),
          first_name: form.first_name,
          last_name: form.last_name,
          specialty: form.specialty || null,
        }),
      });
      setProfessionals((prev) => [...prev, created].sort((a, b) => a.last_name.localeCompare(b.last_name)));
      setForm({ user_id: "", area_id: "", first_name: "", last_name: "", specialty: "" });
      setShowForm(false);
    } catch (err) {
      setCreateError(err instanceof ApiError ? err.message : "Error al crear");
    } finally {
      setCreating(false);
    }
  }

  function handleUpdate(updated: ProfessionalOut) {
    setProfessionals((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
  }

  const existingUserIds = new Set(professionals.map((p) => p.user_id));
  const availableUsers = users.filter((u) => !existingUserIds.has(u.id));

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Profesionales" />

      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
            Equipo profesional
          </h2>
          <Button onClick={() => { setShowForm((v) => !v); setCreateError(null); }}>
            {showForm ? "Cancelar" : "Nuevo profesional"}
          </Button>
        </div>
      </div>

      {showForm && (
        <div className="rounded-2xl border border-brand-200 bg-white p-6 space-y-5 dark:border-brand-800/50 dark:bg-white/[0.03]">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">Nuevo profesional</h3>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <Field label="Usuario del sistema *">
              <select value={form.user_id} onChange={(e) => setField("user_id", e.target.value)} className={inputCls}>
                <option value="">— Seleccionar usuario —</option>
                {availableUsers.map((u) => (
                  <option key={u.id} value={u.id}>{u.full_name} ({u.email})</option>
                ))}
              </select>
            </Field>
            <Field label="Área *">
              <select value={form.area_id} onChange={(e) => setField("area_id", e.target.value)} className={inputCls}>
                <option value="">— Seleccionar área —</option>
                {areas.map((a) => (
                  <option key={a.id} value={a.id}>{AREA_LABELS[a.name] ?? a.name}</option>
                ))}
              </select>
            </Field>
            <Field label="Nombre *">
              <input type="text" value={form.first_name} onChange={(e) => setField("first_name", e.target.value)} placeholder="Nombre" className={inputCls} />
            </Field>
            <Field label="Apellido *">
              <input type="text" value={form.last_name} onChange={(e) => setField("last_name", e.target.value)} placeholder="Apellido" className={inputCls} />
            </Field>
            <Field label="Especialidad">
              <input type="text" value={form.specialty} onChange={(e) => setField("specialty", e.target.value)} placeholder="Especialidad" className={inputCls} />
            </Field>
          </div>
          <div className="flex items-center gap-4">
            {createError && <p role="alert" className="text-sm text-error-500">{createError}</p>}
            <Button onClick={handleCreate} disabled={creating} className="ml-auto">
              {creating ? "Creando..." : "Crear profesional"}
            </Button>
          </div>
        </div>
      )}

      <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] overflow-hidden">
        {loading ? (
          <div className="p-6 text-sm text-gray-400">Cargando...</div>
        ) : professionals.length === 0 ? (
          <div className="p-10 text-center text-sm text-gray-400">Sin profesionales registrados.</div>
        ) : (
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-white/[0.02]">
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Profesional</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Área</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Especialidad</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Estado</th>
              </tr>
            </thead>
            <tbody>
              {professionals.map((p) => (
                <ProfRow key={p.id} prof={p} areas={areas} onUpdate={handleUpdate} />
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
