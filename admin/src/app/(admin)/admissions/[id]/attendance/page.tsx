"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type { AttendanceEntryOut, PresenceStatus, Shift } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";

// ─── Labels & badges ─────────────────────────────────────────────────────────

const PRESENCE_LABELS: Record<PresenceStatus, string> = {
  present: "Presente",
  on_pass: "En permiso",
  external_appointment: "Cita externa",
  hospitalized: "Hospitalizado",
  absent_without_leave: "Ausente sin permiso",
  discharged: "Egresado",
};

const PRESENCE_BADGE: Record<PresenceStatus, string> = {
  present:
    "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400",
  on_pass:
    "bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400",
  external_appointment:
    "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400",
  hospitalized:
    "bg-orange-50 text-orange-700 dark:bg-orange-500/10 dark:text-orange-400",
  absent_without_leave:
    "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400",
  discharged:
    "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
};

const SHIFT_LABELS: Record<Shift, string> = {
  morning: "Mañana",
  afternoon: "Tarde",
  night: "Noche",
};

// The backend returns EntryOut which doesn't carry date/shift directly,
// but roll_call_id can be used for reference. We display what we receive.
export default function AdmissionAttendancePage() {
  const { id } = useParams<{ id: string }>();
  const [entries, setEntries] = useState<AttendanceEntryOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    apiFetch<AttendanceEntryOut[]>(`/admissions/${id}/attendance`)
      .then(setEntries)
      .catch((err) => {
        setError(
          err instanceof ApiError
            ? err.message
            : "Error al cargar el historial"
        );
      })
      .finally(() => setLoading(false));
  }, [id]);

  const awolEntries = entries.filter(
    (e) => e.actual_status === "absent_without_leave"
  );

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Historial de asistencia" />

      <div className="flex items-center justify-between">
        <Link
          href={`/admissions/${id}`}
          className="text-sm text-brand-500 hover:underline"
        >
          &larr; Volver a la admisión
        </Link>
      </div>

      {awolEntries.length > 0 && (
        <div className="rounded-xl border border-error-200 bg-error-50 px-4 py-3 text-sm font-medium text-error-700 dark:border-error-500/30 dark:bg-error-500/10 dark:text-error-400">
          Este residente tiene {awolEntries.length} registro{awolEntries.length > 1 ? "s" : ""} de ausencia sin permiso.
        </div>
      )}

      {error && (
        <p role="alert" className="text-sm text-error-500">
          {error}
        </p>
      )}

      {loading ? (
        <div className="py-12 text-center text-sm text-gray-400">
          Cargando historial...
        </div>
      ) : entries.length === 0 ? (
        <div className="rounded-xl border border-gray-200 bg-white p-8 text-center text-sm text-gray-400 dark:border-gray-800 dark:bg-white/[0.03]">
          No hay registros de asistencia para esta admisión.
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
          <div className="border-b border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-800/50">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-white">
              {entries.length} registro{entries.length !== 1 ? "s" : ""} de asistencia
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-800">
              <thead className="bg-gray-50/50 dark:bg-gray-800/30">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Pase #
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Estado esperado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Estado real
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Nota
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {entries.map((entry) => {
                  const isAwol = entry.actual_status === "absent_without_leave";
                  const hasDiscrepancy =
                    entry.actual_status !== entry.expected_status;

                  return (
                    <tr
                      key={entry.id}
                      className={`transition-colors ${
                        isAwol
                          ? "bg-error-50/60 dark:bg-error-500/5"
                          : hasDiscrepancy
                          ? "bg-warning-50/40 dark:bg-warning-500/5"
                          : "hover:bg-gray-50 dark:hover:bg-white/[0.02]"
                      }`}
                    >
                      <td className="px-4 py-3 text-sm text-gray-500">
                        #{entry.roll_call_id}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${PRESENCE_BADGE[entry.expected_status]}`}
                        >
                          {PRESENCE_LABELS[entry.expected_status]}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${PRESENCE_BADGE[entry.actual_status]}`}
                        >
                          {PRESENCE_LABELS[entry.actual_status]}
                        </span>
                        {isAwol && (
                          <span className="ml-2 text-xs font-semibold text-error-600 dark:text-error-400">
                            Alerta
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {entry.note ?? "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
