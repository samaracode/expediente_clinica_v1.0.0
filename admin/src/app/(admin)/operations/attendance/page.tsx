"use client";

import { useEffect, useState, useCallback } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import type {
  PresenceStatus,
  Shift,
  RosterOut,
  RosterEntryOut,
  RollCallOut,
  AttendanceSummaryOut,
} from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

// ─── Helpers ─────────────────────────────────────────────────────────────────

function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

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

const PRESENCE_STATUS_OPTIONS: PresenceStatus[] = [
  "present",
  "on_pass",
  "external_appointment",
  "hospitalized",
  "absent_without_leave",
  "discharged",
];

// ─── Local row state ──────────────────────────────────────────────────────────

interface RowState {
  admission_id: number;
  resident_name: string;
  expected_status: PresenceStatus;
  actual_status: PresenceStatus;
  note: string;
}

function buildRows(entries: RosterEntryOut[]): RowState[] {
  return entries.map((e) => ({
    admission_id: e.admission_id,
    resident_name: e.resident_name,
    expected_status: e.expected_status,
    actual_status: e.actual_status ?? e.expected_status,
    note: e.note ?? "",
  }));
}

// ─── Summary counter ──────────────────────────────────────────────────────────

function computeLocalSummary(rows: RowState[]): Record<PresenceStatus, number> {
  const counts: Record<PresenceStatus, number> = {
    present: 0,
    on_pass: 0,
    external_appointment: 0,
    hospitalized: 0,
    absent_without_leave: 0,
    discharged: 0,
  };
  for (const row of rows) {
    counts[row.actual_status] += 1;
  }
  return counts;
}

// ─── Página principal ─────────────────────────────────────────────────────────

export default function AttendancePage() {
  const [date, setDate] = useState(todayISO());
  const [shift, setShift] = useState<Shift>("morning");
  const [roster, setRoster] = useState<RosterOut | null>(null);
  const [rows, setRows] = useState<RowState[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // ── Load roster ──────────────────────────────────────────────────────────
  const loadRoster = useCallback(() => {
    setLoading(true);
    setError(null);
    setSavedAt(null);
    const qs = new URLSearchParams({ date, shift });
    apiFetch<RosterOut>(`/attendance/roll-call?${qs}`)
      .then((data) => {
        setRoster(data);
        setRows(buildRows(data.entries));
      })
      .catch((err) => {
        setError(
          err instanceof ApiError ? err.message : "Error al cargar la lista"
        );
      })
      .finally(() => setLoading(false));
  }, [date, shift]);

  useEffect(() => {
    loadRoster();
  }, [loadRoster]);

  // ── Update a single row ──────────────────────────────────────────────────
  function updateRow(
    admissionId: number,
    field: "actual_status" | "note",
    value: string
  ) {
    setRows((prev) =>
      prev.map((r) =>
        r.admission_id === admissionId ? { ...r, [field]: value } : r
      )
    );
  }

  // ── Save roll-call ───────────────────────────────────────────────────────
  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      await apiFetch<RollCallOut>("/attendance/roll-call", {
        method: "POST",
        body: JSON.stringify({
          date,
          shift,
          entries: rows.map((r) => ({
            admission_id: r.admission_id,
            expected_status: r.expected_status,
            actual_status: r.actual_status,
            note: r.note || undefined,
          })),
        }),
      });
      setSavedAt(new Date().toLocaleTimeString("es-CR", { hour: "2-digit", minute: "2-digit" }));
      loadRoster();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Error al guardar el pase"
      );
    } finally {
      setSaving(false);
    }
  }

  // ── Summary ──────────────────────────────────────────────────────────────
  const localCounts = computeLocalSummary(rows);
  const total = rows.length;

  const awolCount = localCounts.absent_without_leave;
  const isAlreadySaved = roster?.roll_call_id != null;

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Pase de asistencia" />

      {/* ── Filtros ──────────────────────────────────────────────────────── */}
      <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="mb-1 block text-xs font-medium uppercase tracking-wider text-gray-500">
              Fecha
            </label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium uppercase tracking-wider text-gray-500">
              Turno
            </label>
            <div className="flex gap-2">
              {(["morning", "afternoon", "night"] as Shift[]).map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setShift(s)}
                  className={`rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
                    shift === s
                      ? "border-brand-500 bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-400"
                      : "border-gray-300 text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400"
                  }`}
                >
                  {SHIFT_LABELS[s]}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Resumen de conteo ─────────────────────────────────────────────── */}
      {rows.length > 0 && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {(
            [
              { key: "present", label: "Presentes" },
              { key: "on_pass", label: "En permiso" },
              { key: "external_appointment", label: "Cita externa" },
              { key: "hospitalized", label: "Hospitalizados" },
              { key: "absent_without_leave", label: "Ausentes" },
              { key: "discharged", label: "Egresados" },
            ] as { key: PresenceStatus; label: string }[]
          ).map(({ key, label }) => (
            <div
              key={key}
              className={`rounded-xl border p-3 text-center ${
                key === "absent_without_leave" && localCounts[key] > 0
                  ? "border-error-200 bg-error-50 dark:border-error-500/30 dark:bg-error-500/10"
                  : "border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
              }`}
            >
              <p
                className={`text-2xl font-bold ${
                  key === "absent_without_leave" && localCounts[key] > 0
                    ? "text-error-600 dark:text-error-400"
                    : "text-gray-800 dark:text-white"
                }`}
              >
                {localCounts[key]}
              </p>
              <p className="mt-0.5 text-xs text-gray-500">{label}</p>
            </div>
          ))}
        </div>
      )}

      {/* ── Total y estado del pase ──────────────────────────────────────── */}
      {rows.length > 0 && (
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="text-sm text-gray-500">
            <span className="font-medium text-gray-700 dark:text-white">{total}</span> residente{total !== 1 ? "s" : ""} activo{total !== 1 ? "s" : ""}{" "}
            {isAlreadySaved && (
              <span className="inline-flex items-center rounded-full bg-success-50 px-2.5 py-0.5 text-xs font-medium text-success-700 dark:bg-success-500/10 dark:text-success-400 ml-2">
                Pase guardado
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            {savedAt && (
              <span className="text-xs text-success-600 dark:text-success-400">
                Guardado a las {savedAt}
              </span>
            )}
            <Button onClick={handleSave} disabled={saving || loading}>
              {saving ? "Guardando..." : isAlreadySaved ? "Actualizar pase" : "Guardar pase"}
            </Button>
          </div>
        </div>
      )}

      {/* ── Alerta de fugas ──────────────────────────────────────────────── */}
      {awolCount > 0 && (
        <div className="rounded-xl border border-error-300 bg-error-50 px-4 py-3 text-sm font-semibold text-error-700 dark:border-error-500/30 dark:bg-error-500/10 dark:text-error-400">
          Alerta: {awolCount} residente{awolCount > 1 ? "s" : ""} marcado{awolCount > 1 ? "s" : ""} como ausente{awolCount > 1 ? "s" : ""} sin permiso.
        </div>
      )}

      {error && (
        <p role="alert" className="text-sm text-error-500">
          {error}
        </p>
      )}

      {/* ── Tabla ────────────────────────────────────────────────────────── */}
      {loading ? (
        <div className="py-12 text-center text-sm text-gray-400">
          Cargando lista...
        </div>
      ) : rows.length === 0 ? (
        <div className="rounded-xl border border-gray-200 bg-white p-8 text-center text-sm text-gray-400 dark:border-gray-800 dark:bg-white/[0.03]">
          No hay residentes activos para esta fecha.
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
          <div className="border-b border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-800/50">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-white">
              {SHIFT_LABELS[shift]} — {new Date(date + "T12:00:00").toLocaleDateString("es-CR", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-800">
              <thead className="bg-gray-50/50 dark:bg-gray-800/30">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Residente
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
                {rows.map((row) => {
                  const hasDiscrepancy = row.actual_status !== row.expected_status;
                  const isAwol = row.actual_status === "absent_without_leave";

                  return (
                    <tr
                      key={row.admission_id}
                      className={`transition-colors ${
                        isAwol
                          ? "bg-error-50/60 dark:bg-error-500/5"
                          : hasDiscrepancy
                          ? "bg-warning-50/40 dark:bg-warning-500/5"
                          : "hover:bg-gray-50 dark:hover:bg-white/[0.02]"
                      }`}
                    >
                      {/* Residente */}
                      <td className="px-4 py-3">
                        <span className="block text-sm font-medium text-gray-800 dark:text-white">
                          {row.resident_name}
                        </span>
                        {isAwol && (
                          <span className="mt-0.5 inline-flex items-center rounded-full bg-error-100 px-2 py-0.5 text-xs font-semibold text-error-700 dark:bg-error-500/20 dark:text-error-400">
                            Alerta de fuga
                          </span>
                        )}
                        {!isAwol && hasDiscrepancy && (
                          <span className="mt-0.5 inline-flex items-center rounded-full bg-warning-100 px-2 py-0.5 text-xs font-medium text-warning-700 dark:bg-warning-500/20 dark:text-warning-400">
                            Discrepancia
                          </span>
                        )}
                      </td>

                      {/* Estado esperado */}
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${PRESENCE_BADGE[row.expected_status]}`}
                        >
                          {PRESENCE_LABELS[row.expected_status]}
                        </span>
                      </td>

                      {/* Selector de estado real */}
                      <td className="px-4 py-3">
                        <select
                          value={row.actual_status}
                          onChange={(e) =>
                            updateRow(
                              row.admission_id,
                              "actual_status",
                              e.target.value
                            )
                          }
                          className={`rounded-lg border px-3 py-1.5 text-sm outline-none focus:border-brand-500 dark:bg-gray-800 dark:text-white ${
                            isAwol
                              ? "border-error-400 bg-error-50 text-error-700 dark:border-error-500/50 dark:bg-error-500/10 dark:text-error-300"
                              : hasDiscrepancy
                              ? "border-warning-400 bg-warning-50 text-warning-700 dark:border-warning-500/50 dark:bg-warning-500/10 dark:text-warning-300"
                              : "border-gray-300 bg-white text-gray-700 dark:border-gray-700"
                          }`}
                        >
                          {PRESENCE_STATUS_OPTIONS.map((s) => (
                            <option key={s} value={s}>
                              {PRESENCE_LABELS[s]}
                            </option>
                          ))}
                        </select>
                      </td>

                      {/* Nota */}
                      <td className="px-4 py-3">
                        <input
                          type="text"
                          value={row.note}
                          onChange={(e) =>
                            updateRow(row.admission_id, "note", e.target.value)
                          }
                          placeholder="Observación..."
                          className="w-full min-w-[160px] rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Botón inferior (duplicado para comodidad en listas largas) ─── */}
      {rows.length > 8 && (
        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={saving || loading}>
            {saving ? "Guardando..." : isAlreadySaved ? "Actualizar pase" : "Guardar pase"}
          </Button>
        </div>
      )}
    </div>
  );
}
