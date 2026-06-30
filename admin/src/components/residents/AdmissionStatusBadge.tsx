import type { AdmissionStatus } from "@/types";

const CONFIG: Record<AdmissionStatus, { label: string; className: string }> = {
  intake_pending:          { label: "Ingreso pendiente",    className: "bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300" },
  consents_pending:        { label: "Consentimientos",      className: "bg-warning-50 text-warning-700 dark:bg-warning-500/15 dark:text-warning-400" },
  assessment_in_progress:  { label: "En evaluación",        className: "bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-400" },
  treatment_active:        { label: "En tratamiento",       className: "bg-success-50 text-success-700 dark:bg-success-500/15 dark:text-success-400" },
  discharged:              { label: "Egresado",             className: "bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400" },
  abandoned:               { label: "Abandonó",             className: "bg-error-50 text-error-700 dark:bg-error-500/15 dark:text-error-400" },
};

export default function AdmissionStatusBadge({ status }: { status: AdmissionStatus }) {
  const { label, className } = CONFIG[status] ?? CONFIG.intake_pending;
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`}>
      {label}
    </span>
  );
}
