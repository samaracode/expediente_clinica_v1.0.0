"use client";

import { useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const ROLE_LABELS: Record<string, string> = {
  admin: "Administrador",
  counselor: "Consejero",
  medical: "Médico",
  social_worker: "Trabajador Social",
  psychologist: "Psicólogo",
  occupational_therapist: "Terapeuta Ocupacional",
  receptionist: "Recepcionista",
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

function ChangePasswordForm() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function handleSubmit() {
    if (!currentPassword || !newPassword) {
      setError("Completá ambos campos.");
      return;
    }
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      await apiFetch("/auth/change-password", {
        method: "POST",
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      });
      setCurrentPassword("");
      setNewPassword("");
      setSuccess(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al cambiar la contraseña");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-5">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">Cambiar contraseña</h3>
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 max-w-xl">
        <Field label="Contraseña actual">
          <input
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            className={inputCls}
          />
        </Field>
        <Field label="Contraseña nueva">
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            className={inputCls}
          />
        </Field>
      </div>
      {error && <p role="alert" className="text-sm text-error-500">{error}</p>}
      {success && <p className="text-sm text-success-600 dark:text-success-400">Contraseña actualizada.</p>}
      <Button onClick={handleSubmit} disabled={saving}>
        {saving ? "Guardando..." : "Cambiar contraseña"}
      </Button>
    </div>
  );
}

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Mi Perfil" />

      <div className="rounded-2xl border border-gray-200 bg-white p-6 space-y-5 dark:border-gray-800 dark:bg-white/[0.03]">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">Mis datos</h3>
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-3 max-w-xl">
          <Field label="Nombre completo">
            <p className="text-sm text-gray-800 dark:text-white">{user?.full_name ?? "—"}</p>
          </Field>
          <Field label="Email">
            <p className="text-sm text-gray-800 dark:text-white">{user?.email ?? "—"}</p>
          </Field>
          <Field label="Rol">
            <p className="text-sm text-gray-800 dark:text-white">
              {user ? (ROLE_LABELS[user.role] ?? user.role) : "—"}
            </p>
          </Field>
        </div>
        <p className="text-xs text-gray-400">
          Para cambiar tu nombre, email o rol, contactá a la persona administradora del sistema.
        </p>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <ChangePasswordForm />
      </div>
    </div>
  );
}
