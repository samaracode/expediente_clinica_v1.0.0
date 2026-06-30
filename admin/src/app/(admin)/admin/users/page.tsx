"use client";

import { useEffect, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import type { UserAdminOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const ROLES = [
  { value: "admin", label: "Administrador" },
  { value: "counselor", label: "Consejero" },
  { value: "medical", label: "Médico" },
  { value: "social_worker", label: "Trabajador Social" },
  { value: "psychologist", label: "Psicólogo" },
  { value: "occupational_therapist", label: "Terapeuta Ocupacional" },
  { value: "receptionist", label: "Recepcionista" },
];

const ROLE_COLORS: Record<string, string> = {
  admin: "bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-400",
  counselor: "bg-brand-50 text-brand-700 dark:bg-brand-900/20 dark:text-brand-400",
  medical: "bg-success-50 text-success-700 dark:bg-success-900/20 dark:text-success-400",
  social_worker: "bg-warning-50 text-warning-700 dark:bg-warning-900/20 dark:text-warning-500",
  psychologist: "bg-pink-50 text-pink-700 dark:bg-pink-900/20 dark:text-pink-400",
  occupational_therapist: "bg-orange-50 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400",
  receptionist: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
};

type NewUserForm = { full_name: string; email: string; role: string; password: string };

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

function UserRow({ user, onUpdate }: { user: UserAdminOut; onUpdate: (u: UserAdminOut) => void }) {
  const [role, setRole] = useState(user.role);
  const [saving, setSaving] = useState(false);

  const roleLabel = ROLES.find((r) => r.value === role)?.label ?? role;

  async function saveRole() {
    setSaving(true);
    try {
      const updated = await apiFetch<UserAdminOut>(`/users/${user.id}`, {
        method: "PUT",
        body: JSON.stringify({ role }),
      });
      onUpdate(updated);
    } finally {
      setSaving(false);
    }
  }

  async function toggleActive() {
    setSaving(true);
    try {
      const updated = await apiFetch<UserAdminOut>(`/users/${user.id}`, {
        method: "PUT",
        body: JSON.stringify({ is_active: !user.is_active }),
      });
      onUpdate(updated);
    } finally {
      setSaving(false);
    }
  }

  return (
    <tr className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-white/[0.02]">
      <td className="px-4 py-3">
        <p className="text-sm font-medium text-gray-800 dark:text-white">{user.full_name}</p>
        <p className="text-xs text-gray-400">{user.email}</p>
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="rounded-lg border border-gray-200 bg-white px-2 py-1 text-xs text-gray-700 focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
          >
            {ROLES.map((r) => (
              <option key={r.value} value={r.value}>{r.label}</option>
            ))}
          </select>
          {role !== user.role && (
            <button
              type="button"
              onClick={saveRole}
              disabled={saving}
              className="text-xs text-brand-500 hover:underline"
            >
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
            user.is_active
              ? "bg-success-50 text-success-700 hover:bg-success-100 dark:bg-success-900/20 dark:text-success-400"
              : "bg-gray-100 text-gray-500 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400"
          }`}
        >
          {user.is_active ? "Activo" : "Inactivo"}
        </button>
      </td>
    </tr>
  );
}

export default function UsersPage() {
  const [users, setUsers] = useState<UserAdminOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<NewUserForm>({ full_name: "", email: "", role: "counselor", password: "" });
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<UserAdminOut[]>("/users/").then(setUsers).finally(() => setLoading(false));
  }, []);

  function setField<K extends keyof NewUserForm>(k: K, v: string) {
    setForm((prev) => ({ ...prev, [k]: v }));
  }

  async function handleCreate() {
    if (!form.full_name || !form.email || !form.password) {
      setCreateError("Nombre, email y contraseña son obligatorios.");
      return;
    }
    setCreating(true);
    setCreateError(null);
    try {
      const created = await apiFetch<UserAdminOut>("/users/", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setUsers((prev) => [...prev, created].sort((a, b) => a.full_name.localeCompare(b.full_name)));
      setForm({ full_name: "", email: "", role: "counselor", password: "" });
      setShowForm(false);
    } catch (err) {
      setCreateError(err instanceof ApiError ? err.message : "Error al crear");
    } finally {
      setCreating(false);
    }
  }

  function handleUpdate(updated: UserAdminOut) {
    setUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
  }

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Usuarios" />

      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
            Gestión de usuarios
          </h2>
          <Button onClick={() => { setShowForm((v) => !v); setCreateError(null); }}>
            {showForm ? "Cancelar" : "Nuevo usuario"}
          </Button>
        </div>
      </div>

      {showForm && (
        <div className="rounded-2xl border border-brand-200 bg-white p-6 space-y-5 dark:border-brand-800/50 dark:bg-white/[0.03]">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">Nuevo usuario</h3>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <Field label="Nombre completo *">
              <input type="text" value={form.full_name} onChange={(e) => setField("full_name", e.target.value)} placeholder="Nombre completo" className={inputCls} />
            </Field>
            <Field label="Email *">
              <input type="email" value={form.email} onChange={(e) => setField("email", e.target.value)} placeholder="correo@ejemplo.com" className={inputCls} />
            </Field>
            <Field label="Rol">
              <select value={form.role} onChange={(e) => setField("role", e.target.value)} className={inputCls}>
                {ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
              </select>
            </Field>
            <Field label="Contraseña *">
              <input type="password" value={form.password} onChange={(e) => setField("password", e.target.value)} placeholder="Mínimo 8 caracteres" className={inputCls} />
            </Field>
          </div>
          <div className="flex items-center gap-4">
            {createError && <p role="alert" className="text-sm text-error-500">{createError}</p>}
            <Button onClick={handleCreate} disabled={creating} className="ml-auto">
              {creating ? "Creando..." : "Crear usuario"}
            </Button>
          </div>
        </div>
      )}

      <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] overflow-hidden">
        {loading ? (
          <div className="p-6 text-sm text-gray-400">Cargando...</div>
        ) : (
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-white/[0.02]">
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Usuario</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Rol</th>
                <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Estado</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <UserRow key={u.id} user={u} onUpdate={handleUpdate} />
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
