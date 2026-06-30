"use client";

import { useEffect, useState, useCallback } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import type {
  DailyPassOut,
  PassEntryOut,
  MedTimeSlotOut,
  AdministrationStatus,
  AllergySeverity,
  UserAdminOut,
} from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

// ─── Helpers ────────────────────────────────────────────────────────────────

function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

function fmtDatetime(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleTimeString("es-CR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

const STATUS_LABELS: Record<AdministrationStatus, string> = {
  pending: "Pendiente",
  taken: "Administrado",
  refused: "Rechazado",
  omitted: "Omitido",
};

const STATUS_BADGE: Record<AdministrationStatus, string> = {
  pending:
    "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400",
  taken: "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400",
  refused: "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400",
  omitted: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
};

const ROUTE_LABELS: Record<string, string> = {
  oral: "Oral",
  IM: "IM",
  SC: "SC",
  otra: "Otra",
};

const ALLERGY_SEVERITY_BADGE: Record<AllergySeverity, string> = {
  leve: "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400",
  moderada: "bg-orange-50 text-orange-700 dark:bg-orange-500/10 dark:text-orange-400",
  severa: "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400",
};

// Texto legible de severidad, tolerante al desajuste front/back
// (el backend devuelve mild/moderate/severe; el front tipa leve/moderada/severa).
const SEVERITY_TEXT: Record<string, string> = {
  mild: "leve",
  moderate: "moderada",
  severe: "severa",
  leve: "leve",
  moderada: "moderada",
  severa: "severa",
};

// ─── Modal de registro de toma ────────────────────────────────────────────

interface RecordModalProps {
  entry: PassEntryOut;
  users: UserAdminOut[];
  onConfirm: (
    status: AdministrationStatus,
    reason: string,
    witnessId: number | null,
    notes: string
  ) => void;
  onCancel: () => void;
  loading: boolean;
}

function RecordModal({
  entry,
  users,
  onConfirm,
  onCancel,
  loading,
}: RecordModalProps) {
  const [status, setStatus] = useState<AdministrationStatus>("taken");
  const [reason, setReason] = useState("");
  const [witnessId, setWitnessId] = useState<number | null>(null);
  const [notes, setNotes] = useState("");

  const needsReason = status === "refused" || status === "omitted";
  const needsWitness = entry.is_controlled;

  function handleSubmit() {
    if (needsReason && !reason.trim()) return;
    if (needsWitness && !witnessId) return;
    onConfirm(status, reason, witnessId, notes);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-gray-900">
        <h3 className="mb-1 text-base font-semibold text-gray-800 dark:text-white">
          Registrar toma
        </h3>
        <p className="mb-4 text-sm text-gray-500">
          <span className="font-medium text-gray-700 dark:text-white">
            {entry.resident_name}
          </span>{" "}
          — {entry.medication_name} {entry.dose}
          {entry.is_controlled && (
            <span className="ml-2 inline-flex items-center rounded-full bg-error-50 px-2 py-0.5 text-xs font-medium text-error-700 dark:bg-error-500/10 dark:text-error-400">
              Controlado
            </span>
          )}
        </p>

        {/* Advertencia de alergias del residente */}
        {entry.allergies.length > 0 && (
          <div className="mb-4 rounded-lg border border-error-300 bg-error-50 px-3 py-2 dark:border-error-500/40 dark:bg-error-500/10">
            <p className="text-sm font-semibold text-error-700 dark:text-error-400">
              ⚠ Alergias del residente
            </p>
            <p className="mt-0.5 text-sm text-error-600 dark:text-error-300">
              {entry.allergies
                .map((a) => a.substance + (a.severity ? ` (${SEVERITY_TEXT[a.severity] ?? a.severity})` : ""))
                .join(", ")}
            </p>
          </div>
        )}

        {/* Estado */}
        <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Estado
        </label>
        <div className="mb-4 flex gap-2">
          {(["taken", "refused", "omitted"] as AdministrationStatus[]).map(
            (s) => (
              <button
                key={s}
                type="button"
                onClick={() => setStatus(s)}
                className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors ${
                  status === s
                    ? "border-brand-500 bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-400"
                    : "border-gray-300 text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400"
                }`}
              >
                {STATUS_LABELS[s]}
              </button>
            )
          )}
        </div>

        {/* Motivo (obligatorio si rechazado/omitido) */}
        {needsReason && (
          <div className="mb-4">
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Motivo <span className="text-error-500">*</span>
            </label>
            <textarea
              rows={2}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Motivo obligatorio..."
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>
        )}

        {/* Testigo (obligatorio si controlado) */}
        {needsWitness && (
          <div className="mb-4">
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Testigo (medicamento controlado) <span className="text-error-500">*</span>
            </label>
            {users.length > 0 ? (
              <select
                value={witnessId ?? ""}
                onChange={(e) =>
                  setWitnessId(e.target.value ? Number(e.target.value) : null)
                }
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
              >
                <option value="">Seleccionar testigo...</option>
                {users.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.full_name}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="number"
                placeholder="ID del testigo"
                value={witnessId ?? ""}
                onChange={(e) =>
                  setWitnessId(e.target.value ? Number(e.target.value) : null)
                }
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
              />
            )}
          </div>
        )}

        {/* Notas opcionales */}
        <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Notas <span className="text-gray-400 font-normal">(opcional)</span>
        </label>
        <textarea
          rows={2}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Observaciones adicionales..."
          className="mb-4 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
        />

        <div className="flex justify-end gap-3">
          <Button variant="outline" size="sm" onClick={onCancel} disabled={loading}>
            Cancelar
          </Button>
          <Button
            size="sm"
            onClick={handleSubmit}
            disabled={
              loading ||
              (needsReason && !reason.trim()) ||
              (needsWitness && !witnessId)
            }
          >
            {loading ? "Guardando..." : "Confirmar"}
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─── Página principal ────────────────────────────────────────────────────────

export default function MedicationsPassPage() {
  const [date, setDate] = useState(todayISO());
  const [slotFilter, setSlotFilter] = useState<number | null>(null);
  const [slots, setSlots] = useState<MedTimeSlotOut[]>([]);
  const [pass, setPass] = useState<DailyPassOut | null>(null);
  const [users, setUsers] = useState<UserAdminOut[]>([]);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState<PassEntryOut | null>(null);
  const [recordLoading, setRecordLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Cargar franjas y lista de usuarios una vez
  useEffect(() => {
    apiFetch<MedTimeSlotOut[]>("/settings/medication-slots")
      .then(setSlots)
      .catch(() => {});
    apiFetch<UserAdminOut[]>("/users/")
      .then(setUsers)
      .catch(() => {});
  }, []);

  const loadPass = useCallback(() => {
    setLoading(true);
    setError(null);
    const qs = new URLSearchParams({ date });
    if (slotFilter) qs.set("slot", String(slotFilter));
    apiFetch<DailyPassOut>(`/medications/pass?${qs}`)
      .then(setPass)
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Error al cargar el pase");
      })
      .finally(() => setLoading(false));
  }, [date, slotFilter]);

  useEffect(() => {
    loadPass();
  }, [loadPass]);

  async function handleRecord(
    status: AdministrationStatus,
    reason: string,
    witnessId: number | null,
    notes: string
  ) {
    if (!recording) return;
    setRecordLoading(true);
    setError(null);
    try {
      await apiFetch(
        `/medication-administrations/${recording.administration_id}/record`,
        {
          method: "POST",
          body: JSON.stringify({
            status,
            reason: reason || undefined,
            witness_user_id: witnessId || undefined,
            notes: notes || undefined,
          }),
        }
      );
      setRecording(null);
      loadPass();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al registrar toma");
    } finally {
      setRecordLoading(false);
    }
  }

  // Agrupar entradas por franja
  const grouped = (() => {
    if (!pass) return [];
    const map = new Map<string, PassEntryOut[]>();
    for (const entry of pass.entries) {
      const key = entry.slot_label ?? "Sin franja";
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(entry);
    }
    return Array.from(map.entries());
  })();

  const overdueCount = pass?.entries.filter(
    (e) => e.is_overdue && e.status === "pending"
  ).length ?? 0;

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Pase de medicamentos" />

      {/* Filtros */}
      <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500 uppercase tracking-wider">
              Fecha
            </label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>
          {slots.length > 0 && (
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-500 uppercase tracking-wider">
                Franja
              </label>
              <select
                value={slotFilter ?? ""}
                onChange={(e) =>
                  setSlotFilter(e.target.value ? Number(e.target.value) : null)
                }
                className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
              >
                <option value="">Todas las franjas</option>
                {slots.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.label} ({s.time.slice(0, 5)})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Banner de vencidas */}
      {overdueCount > 0 && (
        <div className="rounded-xl border border-error-200 bg-error-50 px-4 py-3 text-sm font-medium text-error-700 dark:border-error-500/30 dark:bg-error-500/10 dark:text-error-400">
          Hay {overdueCount} dosis vencida{overdueCount > 1 ? "s" : ""} sin registrar.
        </div>
      )}

      {error && (
        <p role="alert" className="text-sm text-error-500">{error}</p>
      )}

      {/* Tabla agrupada por franja */}
      {loading ? (
        <div className="py-12 text-center text-sm text-gray-400">Cargando pase...</div>
      ) : grouped.length === 0 ? (
        <div className="rounded-xl border border-gray-200 bg-white p-8 text-center text-sm text-gray-400 dark:border-gray-800 dark:bg-white/[0.03]">
          No hay tomas programadas para esta fecha.
        </div>
      ) : (
        grouped.map(([slotLabel, entries]) => (
          <div
            key={slotLabel}
            className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]"
          >
            <div className="border-b border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-800/50">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-white">
                {slotLabel}
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
                      Medicamento
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Dosis / Vía
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Hora pautada
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                      Estado
                    </th>
                    <th className="px-4 py-3" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {entries.map((entry) => (
                    <tr
                      key={entry.administration_id}
                      className={`hover:bg-gray-50 dark:hover:bg-white/[0.02] ${
                        entry.is_overdue && entry.status === "pending"
                          ? "bg-error-50/40 dark:bg-error-500/5"
                          : ""
                      }`}
                    >
                      <td className="px-4 py-3">
                        <span className="block text-sm font-medium text-gray-800 dark:text-white">
                          {entry.resident_name}
                        </span>
                        {entry.allergies.length > 0 && (
                          <div className="mt-1 flex flex-wrap gap-1">
                            {entry.allergies.map((allergy) => (
                              <span
                                key={allergy.id}
                                className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                                  allergy.severity
                                    ? ALLERGY_SEVERITY_BADGE[allergy.severity]
                                    : "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400"
                                }`}
                              >
                                ⚠ Alérgico: {allergy.substance}
                              </span>
                            ))}
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700 dark:text-white">
                        <span>{entry.medication_name}</span>
                        {entry.is_controlled && (
                          <span className="ml-2 inline-flex items-center rounded-full bg-error-50 px-2 py-0.5 text-xs font-medium text-error-700 dark:bg-error-500/10 dark:text-error-400">
                            Controlado
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {entry.dose} — {ROUTE_LABELS[entry.route] ?? entry.route}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        <span
                          className={
                            entry.is_overdue && entry.status === "pending"
                              ? "font-semibold text-error-600 dark:text-error-400"
                              : ""
                          }
                        >
                          {fmtDatetime(entry.scheduled_at)}
                          {entry.is_overdue && entry.status === "pending" && " ⚠"}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_BADGE[entry.status]}`}
                        >
                          {STATUS_LABELS[entry.status]}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        {entry.status === "pending" && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setRecording(entry)}
                          >
                            Registrar toma
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))
      )}

      {recording && (
        <RecordModal
          entry={recording}
          users={users}
          onConfirm={handleRecord}
          onCancel={() => setRecording(null)}
          loading={recordLoading}
        />
      )}
    </div>
  );
}
