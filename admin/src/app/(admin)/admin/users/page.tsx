"use client";

import { useEffect, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import type { Module, UserAdminOut } from "@/types";
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

// ADR 0003: acceso por-usuario, no por-rol. El admin marca estos checkboxes
// al crear/editar cada usuario. "admin" no aparece aquí: tiene acceso total
// implícito y no es editable (evita que se bloquee a sí mismo).
const MODULES: { value: Module; label: string }[] = [
  { value: "residents", label: "Clínica / Residentes" },
  { value: "operations", label: "Operación (medicamentos, asistencia, ocupación, turno)" },
  { value: "finance", label: "Finanzas" },
  { value: "reports", label: "Reportes" },
  { value: "medical", label: "Evaluación Médica" },
  { value: "psychology", label: "Evaluación Psicológica" },
  { value: "therapeutic", label: "Evaluación Terapéutica" },
  { value: "social_work", label: "Trabajo Social" },
  { value: "occupational_therapy", label: "Terapia Ocupacional" },
];

type NewUserForm = { full_name: string; email: string; role: string; password: string; modules: Module[] };

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

function ModuleCheckboxes({
  selected,
  onChange,
  disabled,
}: {
  selected: Module[];
  onChange: (modules: Module[]) => void;
  disabled?: boolean;
}) {
  function toggle(m: Module) {
    if (selected.includes(m)) onChange(selected.filter((x) => x !== m));
    else onChange([...selected, m]);
  }
  return (
    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
      {MODULES.map((m) => (
        <label key={m.value} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <input
            type="checkbox"
            checked={selected.includes(m.value)}
            onChange={() => toggle(m.value)}
            disabled={disabled}
            className="h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
          />
          {m.label}
        </label>
      ))}
    </div>
  );
}

function ResetPasswordModal({ userId, onClose }: { userId: number; onClose: () => void }) {
  const [newPassword, setNewPassword] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  async function handleReset() {
    if (!newPassword) {
      setError("Escribí la nueva contraseña temporal.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await apiFetch(`/users/${userId}/reset-password`, {
        method: "POST",
        body: JSON.stringify({ new_password: newPassword }),
      });
      setDone(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al restablecer");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-sm rounded-2xl border border-gray-200 bg-white p-6 space-y-4 dark:border-gray-800 dark:bg-gray-900">
        <h3 className="text-sm font-semibold text-gray-800 dark:text-white">Restablecer contraseña</h3>
        {done ? (
          <>
            <p className="text-sm text-success-600 dark:text-success-400">
              Contraseña actualizada. Comuníquele la nueva contraseña temporal a la persona.
            </p>
            <Button onClick={onClose} className="w-full">Cerrar</Button>
          </>
        ) : (
          <>
            <Field label="Nueva contraseña temporal">
              <input
                type="text"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Contraseña temporal"
                className={inputCls}
              />
            </Field>
            {error && <p role="alert" className="text-sm text-error-500">{error}</p>}
            <div className="flex justify-end gap-2">
              <button type="button" onClick={onClose} className="text-sm text-gray-500 hover:underline">
                Cancelar
              </button>
              <Button onClick={handleReset} disabled={saving}>
                {saving ? "Guardando..." : "Restablecer"}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function UserRow({ user, onUpdate }: { user: UserAdminOut; onUpdate: (u: UserAdminOut) => void }) {
  const [role, setRole] = useState(user.role);
  const [modules, setModules] = useState<Module[]>(user.modules);
  const [saving, setSaving] = useState(false);
  const [editingModules, setEditingModules] = useState(false);
  const [resetting, setResetting] = useState(false);

  const isAdmin = user.role === "admin";
  const modulesChanged = JSON.stringify([...modules].sort()) !== JSON.stringify([...user.modules].sort());

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

  async function saveModules() {
    setSaving(true);
    try {
      const updated = await apiFetch<UserAdminOut>(`/users/${user.id}`, {
        method: "PUT",
        body: JSON.stringify({ modules }),
      });
      onUpdate(updated);
      setEditingModules(false);
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
    <tr className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-white/[0.02] align-top">
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
        {isAdmin ? (
          <span className="text-xs text-gray-400">Acceso total (fijo)</span>
        ) : editingModules ? (
          <div className="space-y-2 max-w-xs">
            <ModuleCheckboxes selected={modules} onChange={setModules} disabled={saving} />
            <div className="flex gap-2">
              <button type="button" onClick={saveModules} disabled={saving} className="text-xs text-brand-500 hover:underline">
                Guardar
              </button>
              <button
                type="button"
                onClick={() => { setModules(user.modules); setEditingModules(false); }}
                className="text-xs text-gray-400 hover:underline"
              >
                Cancelar
              </button>
            </div>
          </div>
        ) : (
          <button type="button" onClick={() => setEditingModules(true)} className="text-left">
            {user.modules.length === 0 ? (
              <span className="text-xs text-gray-400 hover:underline">Sin módulos — editar</span>
            ) : (
              <span className="text-xs text-gray-600 dark:text-gray-300 hover:underline">
                {user.modules.length} módulo{user.modules.length !== 1 ? "s" : ""} — editar
              </span>
            )}
          </button>
        )}
        {modulesChanged && !editingModules && (
          <p className="text-xs text-warning-600">Cambios sin guardar</p>
        )}
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
      <td className="px-4 py-3">
        <button type="button" onClick={() => setResetting(true)} className="text-xs text-brand-500 hover:underline">
          Restablecer contraseña
        </button>
        {resetting && <ResetPasswordModal userId={user.id} onClose={() => setResetting(false)} />}
      </td>
    </tr>
  );
}

export default function UsersPage() {
  const [users, setUsers] = useState<UserAdminOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<NewUserForm>({ full_name: "", email: "", role: "counselor", password: "", modules: [] });
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<UserAdminOut[]>("/users/").then(setUsers).finally(() => setLoading(false));
  }, []);

  function setField<K extends keyof NewUserForm>(k: K, v: NewUserForm[K]) {
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
      setForm({ full_name: "", email: "", role: "counselor", password: "", modules: [] });
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
              <input type="password" value={form.password} onChange={(e) => setField("password", e.target.value)} placeholder="Contraseña temporal" className={inputCls} />
            </Field>
          </div>
          {form.role === "admin" ? (
            <p className="text-sm text-gray-400">El rol Administrador tiene acceso total a todos los módulos (fijo, no editable).</p>
          ) : (
            <Field label="Módulos habilitados">
              <ModuleCheckboxes selected={form.modules} onChange={(m) => setField("modules", m)} />
            </Field>
          )}
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
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-white/[0.02]">
                  <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Usuario</th>
                  <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Rol</th>
                  <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Módulos</th>
                  <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Estado</th>
                  <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Contraseña</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <UserRow key={u.id} user={u} onUpdate={handleUpdate} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
