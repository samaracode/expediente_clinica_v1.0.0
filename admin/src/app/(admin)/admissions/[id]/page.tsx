"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { AdmissionOut, ResidentOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import AdmissionStatusBadge from "@/components/residents/AdmissionStatusBadge";

const SECTIONS: Array<{ key: string; label: string; href: (id: string) => string; active: boolean }> = [
  { key: "consents", label: "Consentimientos", href: (id) => `/admissions/${id}/consents`, active: true },
  { key: "personal_items", label: "Inventario de pertenencias", href: (id) => `/admissions/${id}/personal-items`, active: true },
  { key: "economic_situation", label: "Situación económica", href: (id) => `/admissions/${id}/economic-situation`, active: true },
  { key: "medical", label: "Evaluación médica", href: (id) => `/admissions/${id}/medical`, active: true },
  { key: "therapeutic", label: "Evaluación terapéutica", href: (id) => `/admissions/${id}/therapeutic`, active: true },
  { key: "social_work", label: "Trabajo social", href: (id) => `/admissions/${id}/social-work`, active: true },
  { key: "psychology", label: "Psicología", href: (id) => `/admissions/${id}/psychology`, active: true },
  { key: "occupational_therapy", label: "Terapia ocupacional", href: (id) => `/admissions/${id}/occupational-therapy`, active: true },
  { key: "treatment_plan", label: "Plan de tratamiento", href: (id) => `/admissions/${id}/treatment-plan`, active: true },
  { key: "exit_passes", label: "Permisos de salida", href: () => "#", active: false },
  { key: "daily_logs", label: "Notas diarias", href: () => "#", active: false },
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
  const [admission, setAdmission] = useState<AdmissionOut | null>(null);
  const [resident, setResident] = useState<ResidentOut | null>(null);
  const [loading, setLoading] = useState(true);

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
          <AdmissionStatusBadge status={admission.status} />
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
            const card = (
              <div
                className={`rounded-xl border p-4 transition-colors ${
                  section.active
                    ? "border-gray-200 bg-white hover:border-brand-300 hover:bg-brand-50 dark:border-gray-800 dark:bg-white/[0.03] cursor-pointer"
                    : "border-gray-100 bg-gray-50 opacity-50 cursor-not-allowed dark:border-gray-800 dark:bg-white/[0.01]"
                }`}
              >
                <p className="text-sm font-medium text-gray-800 dark:text-white">{section.label}</p>
                {!section.active && (
                  <p className="mt-0.5 text-xs text-gray-400">Próximamente</p>
                )}
              </div>
            );

            return section.active ? (
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
