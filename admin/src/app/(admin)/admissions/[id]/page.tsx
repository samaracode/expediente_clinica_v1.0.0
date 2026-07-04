"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { AdmissionOut, AdmissionStatus, ResidentOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import AdmissionStatusBadge from "@/components/residents/AdmissionStatusBadge";
import { useAuth } from "@/context/AuthContext";

const SECTIONS: Array<{ key: string; label: string; href: (id: string) => string; active: boolean; restrictedPath?: string }> = [
  { key: "consents", label: "Consentimientos", href: (id) => `/admissions/${id}/consents`, active: true },
  { key: "personal_items", label: "Inventario de pertenencias", href: (id) => `/admissions/${id}/personal-items`, active: true },
  { key: "economic_situation", label: "Situación económica", href: (id) => `/admissions/${id}/economic-situation`, active: true },
  { key: "medical", label: "Evaluación médica", href: (id) => `/admissions/${id}/medical`, active: true, restrictedPath: "/medical" },
  { key: "therapeutic", label: "Evaluación terapéutica", href: (id) => `/admissions/${id}/therapeutic`, active: true, restrictedPath: "/therapeutic" },
  { key: "social_work", label: "Trabajo social", href: (id) => `/admissions/${id}/social-work`, active: true, restrictedPath: "/social-work" },
  { key: "psychology", label: "Psicología", href: (id) => `/admissions/${id}/psychology`, active: true, restrictedPath: "/psychology" },
  { key: "occupational_therapy", label: "Terapia ocupacional", href: (id) => `/admissions/${id}/occupational-therapy`, active: true, restrictedPath: "/occupational-therapy" },
  { key: "treatment_plan", label: "Plan de tratamiento", href: (id) => `/admissions/${id}/treatment-plan`, active: true },
  { key: "medications", label: "Medicamentos", href: (id) => `/admissions/${id}/medications`, active: true },
  { key: "exit_passes", label: "Permisos de salida", href: (id) => `/admissions/${id}/exit-passes`, active: true },
  { key: "daily_logs", label: "Notas diarias", href: (id) => `/admissions/${id}/daily-logs`, active: true },
  { key: "consultations", label: "Consultas de seguimiento", href: (id) => `/admissions/${id}/consultations`, active: true },
  { key: "attendance", label: "Historial de asistencia", href: (id) => `/admissions/${id}/attendance`, active: true },
  { key: "finance", label: "Control financiero", href: (id) => `/admissions/${id}/finance`, active: true, restrictedPath: "/finance" },
];

const STATUS_LABELS: Record<string, string> = {
  intake_pending: "Pendiente de ingreso",
  consents_pending: "Consentimientos pendientes",
  assessment_in_progress: "Evaluación en progreso",
  treatment_active: "Tratamiento activo",
  discharged: "Egresado",
  abandoned: "Abandono",
};

export default function AdmissionHubPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [admission, setAdmission] = useState<AdmissionOut | null>(null);
  const [resident, setResident] = useState<ResidentOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [confirmArchive, setConfirmArchive] = useState(false);
  const [archiving, setArchiving] = useState(false);
  const [editingStatus, setEditingStatus] = useState(false);
  const [pendingStatus, setPendingStatus] = useState<AdmissionStatus | null>(null);
  const [savingStatus, setSavingStatus] = useState(false);
  const { hasAccess, user } = useAuth();

  async function handleArchive() {
    setArchiving(true);
    try {
      await apiFetch(`/admissions/${id}`, { method: "DELETE" });
      router.push(resident ? `/residents/${resident.id}` : "/residents");
    } finally {
      setArchiving(false);
    }
  }

  async function handleConfirmStatusChange() {
    if (!pendingStatus) return;
    setSavingStatus(true);
    try {
      const updated = await apiFetch<AdmissionOut>(`/admissions/${id}/status`, {
        method: "PUT",
        body: JSON.stringify({ status: pendingStatus }),
      });
      setAdmission(updated);
      setEditingStatus(false);
      setPendingStatus(null);
    } finally {
      setSavingStatus(false);
    }
  }

  useEffect(() => {
    apiFetch<AdmissionOut>(`/admissions/${id}`)
      .then(async (a) => {
        setAdmission(a);
        const r = await apiFetch<ResidentOut>(`/residents/${a.resident_id}`);
        setResident(r);
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="p-6 text-sm text-gray-400">Cargando...</div>;
  if (!admission) return <div className="p-6 text-sm text-error-500">Admisión no encontrada.</div>;

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle={`Admisión ${admission.admission_number}`} />

      {/* Header */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-xs font-mono text-gray-400">{admission.admission_number}</p>
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white">
              {resident ? `${resident.first_name} ${resident.last_name}` : `Residente #${admission.resident_id}`}
            </h2>
            {resident && (
              <Link href={`/residents/${resident.id}`} className="text-xs text-brand-500 hover:underline">
                Ver perfil del residente
              </Link>
            )}
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            {!editingStatus ? (
              <button
                onClick={() => { setPendingStatus(admission.status); setEditingStatus(true); }}
                className="rounded-full transition-opacity hover:opacity-80"
                title="Cambiar estado de la admisión"
              >
                <AdmissionStatusBadge status={admission.status} />
              </button>
            ) : (
              <span className="flex items-center gap-1.5">
                <select
                  value={pendingStatus ?? admission.status}
                  onChange={(e) => setPendingStatus(e.target.value as AdmissionStatus)}
                  disabled={savingStatus}
                  className="rounded-lg border border-gray-300 bg-white px-2 py-1 text-xs text-gray-700 focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
                >
                  {(Object.entries(STATUS_LABELS) as [AdmissionStatus, string][]).map(([v, l]) => (
                    <option key={v} value={v}>{l}</option>
                  ))}
                </select>
                {pendingStatus !== admission.status ? (
                  <button
                    onClick={handleConfirmStatusChange}
                    disabled={savingStatus}
                    className="rounded px-2 py-1 text-xs font-medium bg-brand-500 text-white hover:bg-brand-600 disabled:opacity-50"
                  >
                    {savingStatus ? "Guardando..." : "Confirmar"}
                  </button>
                ) : null}
                <button
                  onClick={() => { setEditingStatus(false); setPendingStatus(null); }}
                  disabled={savingStatus}
                  className="rounded px-2 py-1 text-xs font-medium border border-gray-300 text-gray-600 hover:bg-gray-50"
                >
                  Cancelar
                </button>
              </span>
            )}
            <button
              onClick={() => window.open(`/api/v1/admissions/${id}/export/pdf`, "_blank")}
              className="rounded px-3 py-1.5 text-xs font-medium border border-gray-300 text-gray-600 hover:bg-gray-50 flex items-center gap-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3M3 17v3a1 1 0 001 1h16a1 1 0 001-1v-3M3 17H1m2 0h18m0 0h2" />
              </svg>
              Exportar PDF
            </button>
            {user?.role === "admin" && !admission.is_deleted && (
              confirmArchive ? (
                <span className="flex items-center gap-1 text-sm">
                  <span className="text-gray-500">¿Confirmar?</span>
                  <button
                    onClick={handleArchive}
                    disabled={archiving}
                    className="rounded px-2 py-1 text-xs font-medium bg-error-500 text-white hover:bg-error-600 disabled:opacity-50"
                  >
                    {archiving ? "Archivando..." : "Sí, archivar"}
                  </button>
                  <button
                    onClick={() => setConfirmArchive(false)}
                    className="rounded px-2 py-1 text-xs font-medium border border-gray-300 text-gray-600 hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                </span>
              ) : (
                <button
                  onClick={() => setConfirmArchive(true)}
                  className="rounded px-2 py-1 text-xs font-medium border border-gray-300 text-gray-600 hover:bg-gray-50"
                >
                  Archivar admisión
                </button>
              )
            )}
          </div>
        </div>

        <dl className="mt-4 grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-3 text-sm">
          <div>
            <dt className="text-gray-400">Fecha de ingreso</dt>
            <dd className="text-gray-700 dark:text-white">
              {new Date(admission.admission_date).toLocaleDateString("es-CR")}
            </dd>
          </div>
          <div>
            <dt className="text-gray-400">Tipo</dt>
            <dd className="text-gray-700 dark:text-white">
              {admission.admission_type === "first" ? "Primera vez" : "Reingreso"}
            </dd>
          </div>
          <div>
            <dt className="text-gray-400">Estado</dt>
            <dd className="text-gray-700 dark:text-white">
              {STATUS_LABELS[admission.status] ?? admission.status}
            </dd>
          </div>
          {admission.referral_source && (
            <div>
              <dt className="text-gray-400">Referido por</dt>
              <dd className="text-gray-700 dark:text-white">{admission.referral_source}</dd>
            </div>
          )}
          {admission.sponsor_name && (
            <div>
              <dt className="text-gray-400">Patrocinador</dt>
              <dd className="text-gray-700 dark:text-white">{admission.sponsor_name}</dd>
            </div>
          )}
        </dl>
      </div>

      {/* Secciones del expediente */}
      <div>
        <h3 className="mb-3 text-sm font-medium text-gray-500 uppercase tracking-wider">
          Secciones del expediente
        </h3>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {SECTIONS.map((section) => {
            const href = section.href(id);
            const accessible = section.active && (!section.restrictedPath || hasAccess(section.restrictedPath));
            const card = (
              <div
                className={`rounded-xl border p-4 transition-colors ${
                  accessible
                    ? "border-gray-200 bg-white hover:border-brand-300 hover:bg-brand-50 dark:border-gray-800 dark:bg-white/[0.03] cursor-pointer"
                    : "border-gray-100 bg-gray-50 opacity-50 cursor-not-allowed dark:border-gray-800 dark:bg-white/[0.01]"
                }`}
              >
                <p className="text-sm font-medium text-gray-800 dark:text-white">{section.label}</p>
                {!section.active && (
                  <p className="mt-0.5 text-xs text-gray-400">Próximamente</p>
                )}
                {section.active && section.restrictedPath && !hasAccess(section.restrictedPath) && (
                  <p className="mt-0.5 text-xs text-gray-400">Sin acceso</p>
                )}
              </div>
            );

            return accessible ? (
              <Link key={section.key} href={href}>
                {card}
              </Link>
            ) : (
              <div key={section.key}>{card}</div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
