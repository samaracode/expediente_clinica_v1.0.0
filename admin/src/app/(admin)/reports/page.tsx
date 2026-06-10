"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { AdmissionReportRow, ConsultationReportRow, TreatmentProgressRow } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";

type Tab = "admissions" | "consultations" | "progress";

const ADMISSION_STATUS_LABELS: Record<string, string> = {
  intake_pending: "Pendiente ingreso",
  consents_pending: "Consentimientos pendientes",
  assessment_in_progress: "Evaluación en progreso",
  treatment_active: "Tratamiento activo",
  discharged: "Egresado",
  abandoned: "Abandono",
};

const ADMISSION_TYPE_LABELS: Record<string, string> = {
  first: "Primera vez",
  readmission: "Reingreso",
};

const STAGE_LABELS: Record<string, string> = {
  orientation: "Orientación",
  adaptation: "Adaptación",
  development: "Desarrollo",
  consolidation: "Consolidación",
  reintegration: "Reinserción",
};

const STATUS_COLORS: Record<string, string> = {
  intake_pending: "bg-gray-100 text-gray-600",
  consents_pending: "bg-warning-50 text-warning-700",
  assessment_in_progress: "bg-brand-50 text-brand-700",
  treatment_active: "bg-success-50 text-success-700",
  discharged: "bg-gray-100 text-gray-500",
  abandoned: "bg-error-50 text-error-700",
};

const AREA_LABELS: Record<string, string> = {
  medicine: "Medicina",
  therapeutic: "Terapéutica",
  social_work: "Trabajo Social",
  psychology: "Psicología",
  occupational_therapy: "T. Ocupacional",
};

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-t-lg px-5 py-2.5 text-sm font-medium transition-colors border-b-2 ${
        active
          ? "border-brand-500 text-brand-600 dark:text-brand-400"
          : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
      }`}
    >
      {children}
    </button>
  );
}

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState<Tab>("admissions");
  const [admissions, setAdmissions] = useState<AdmissionReportRow[]>([]);
  const [consultations, setConsultations] = useState<ConsultationReportRow[]>([]);
  const [progress, setProgress] = useState<TreatmentProgressRow[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        if (activeTab === "admissions" && admissions.length === 0) {
          const data = await apiFetch<AdmissionReportRow[]>("/reports/admissions");
          setAdmissions(data);
        } else if (activeTab === "consultations" && consultations.length === 0) {
          const data = await apiFetch<ConsultationReportRow[]>("/reports/consultations");
          setConsultations(data);
        } else if (activeTab === "progress" && progress.length === 0) {
          const data = await apiFetch<TreatmentProgressRow[]>("/reports/treatment-progress");
          setProgress(data);
        }
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [activeTab]);

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Reportes" />

      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Reportes clínicos</h2>
        <p className="text-sm text-gray-500 mt-1">Vista general de admisiones, consultas y progreso de tratamiento.</p>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] overflow-hidden">
        {/* Tabs */}
        <div className="flex border-b border-gray-200 px-4 dark:border-gray-800">
          <TabButton active={activeTab === "admissions"} onClick={() => setActiveTab("admissions")}>
            Ingresos
          </TabButton>
          <TabButton active={activeTab === "consultations"} onClick={() => setActiveTab("consultations")}>
            Consultas
          </TabButton>
          <TabButton active={activeTab === "progress"} onClick={() => setActiveTab("progress")}>
            Progreso de tratamiento
          </TabButton>
        </div>

        {loading ? (
          <div className="p-8 text-center text-sm text-gray-400">Cargando...</div>
        ) : (
          <div className="overflow-x-auto">
            {activeTab === "admissions" && (
              admissions.length === 0 ? (
                <div className="p-8 text-center text-sm text-gray-400">Sin datos.</div>
              ) : (
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-gray-100 bg-gray-50 dark:border-gray-800 dark:bg-white/[0.02]">
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Número</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Residente</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Ingreso</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Tipo</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Estado</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Egreso</th>
                    </tr>
                  </thead>
                  <tbody>
                    {admissions.map((row) => (
                      <tr key={row.id} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-white/[0.02]">
                        <td className="px-4 py-3">
                          <Link href={`/admissions/${row.id}`} className="text-xs font-mono text-brand-500 hover:underline">
                            {row.admission_number}
                          </Link>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-700 dark:text-white">{row.resident_name}</td>
                        <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-300">
                          {new Date(row.admission_date + "T12:00:00").toLocaleDateString("es-CR")}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-300">
                          {ADMISSION_TYPE_LABELS[row.admission_type] ?? row.admission_type}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLORS[row.status] ?? "bg-gray-100 text-gray-600"}`}>
                            {ADMISSION_STATUS_LABELS[row.status] ?? row.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">
                          {row.discharge_date ? new Date(row.discharge_date + "T12:00:00").toLocaleDateString("es-CR") : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )
            )}

            {activeTab === "consultations" && (
              consultations.length === 0 ? (
                <div className="p-8 text-center text-sm text-gray-400">Sin consultas registradas.</div>
              ) : (
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-gray-100 bg-gray-50 dark:border-gray-800 dark:bg-white/[0.02]">
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Fecha</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Residente</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Profesional</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Área</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Tipo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {consultations.map((row) => (
                      <tr key={row.id} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-white/[0.02]">
                        <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-300">
                          {new Date(row.consultation_date + "T12:00:00").toLocaleDateString("es-CR")}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-700 dark:text-white">{row.resident_name}</td>
                        <td className="px-4 py-3 text-sm text-gray-700 dark:text-white">{row.professional_name}</td>
                        <td className="px-4 py-3">
                          {row.area_name && (
                            <span className="rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-medium text-brand-700 dark:bg-brand-900/20 dark:text-brand-400">
                              {AREA_LABELS[row.area_name] ?? row.area_name}
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">{row.consultation_type ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )
            )}

            {activeTab === "progress" && (
              progress.length === 0 ? (
                <div className="p-8 text-center text-sm text-gray-400">Sin tratamientos activos.</div>
              ) : (
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-gray-100 bg-gray-50 dark:border-gray-800 dark:bg-white/[0.02]">
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Admisión</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Residente</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Estado</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Etapa actual</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-500">Progreso</th>
                    </tr>
                  </thead>
                  <tbody>
                    {progress.map((row) => (
                      <tr key={row.admission_id} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-white/[0.02]">
                        <td className="px-4 py-3">
                          <Link href={`/admissions/${row.admission_id}`} className="text-xs font-mono text-brand-500 hover:underline">
                            {row.admission_number}
                          </Link>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-700 dark:text-white">{row.resident_name}</td>
                        <td className="px-4 py-3">
                          <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLORS[row.status] ?? "bg-gray-100 text-gray-600"}`}>
                            {ADMISSION_STATUS_LABELS[row.status] ?? row.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-700 dark:text-white">
                          {row.current_stage ? (STAGE_LABELS[row.current_stage] ?? row.current_stage) : "—"}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-2 rounded-full bg-gray-100 dark:bg-gray-800 overflow-hidden" style={{ minWidth: 80 }}>
                              <div
                                className="h-full rounded-full bg-brand-500"
                                style={{ width: `${(row.stages_completed / row.stages_total) * 100}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-500 whitespace-nowrap">
                              {row.stages_completed}/{row.stages_total}
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
}
