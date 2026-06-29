"use client";

import { useEffect, useState, useCallback } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import type {
  OccupancyOut,
  CapacityOut,
  WaitlistEntryOut,
  WaitlistEntryCreate,
  WaitlistEntryPatch,
  WaitlistStatus,
} from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

// ─── Labels & badges ──────────────────────────────────────────────────────────

const WAITLIST_STATUS_LABELS: Record<WaitlistStatus, string> = {
  waiting: "En espera",
  admitted: "Admitido",
  declined: "Rechazado",
  cancelled: "Cancelado",
};

const WAITLIST_STATUS_BADGE: Record<WaitlistStatus, string> = {
  waiting:
    "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400",
  admitted:
    "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400",
  declined:
    "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400",
  cancelled:
    "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
};

const STATUS_KEY_LABELS: Record<string, string> = {
  treatment_active: "En tratamiento",
  intake_pending: "Ingreso pendiente",
  consents_pending: "Consentimientos pendientes",
  assessment_in_progress: "Valoración",
  discharged: "Egresado",
  abandoned: "Abandonó",
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

function fmtDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso + "T12:00:00").toLocaleDateString("es-CR", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function occupancyColor(ratio: number): string {
  if (ratio < 0.7) return "bg-success-500";
  if (ratio < 0.9) return "bg-warning-500";
  return "bg-error-500";
}

function occupancyTextColor(ratio: number): string {
  if (ratio < 0.7) return "text-success-700 dark:text-success-400";
  if (ratio < 0.9) return "text-warning-700 dark:text-warning-400";
  return "text-error-700 dark:text-error-400";
}

// ─── Modal: Agregar a lista de espera ────────────────────────────────────────

interface AddWaitlistModalProps {
  onConfirm: (data: WaitlistEntryCreate) => Promise<void>;
  onCancel: () => void;
  loading: boolean;
}

function AddWaitlistModal({ onConfirm, onCancel, loading }: AddWaitlistModalProps) {
  const [fullName, setFullName] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [requestedAt, setRequestedAt] = useState(
    new Date().toISOString().slice(0, 10)
  );
  const [referredBy, setReferredBy] = useState("");
  const [notes, setNotes] = useState("");

  function handleSubmit() {
    if (!fullName.trim()) return;
    onConfirm({
      full_name: fullName.trim(),
      contact_phone: contactPhone.trim() || undefined,
      contact_email: contactEmail.trim() || undefined,
      requested_at: requestedAt || undefined,
      referred_by: referredBy.trim() || undefined,
      notes: notes.trim() || undefined,
    });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl dark:bg-gray-900">
        <h3 className="mb-4 text-base font-semibold text-gray-800 dark:text-white">
          Agregar a lista de espera
        </h3>

        <div className="space-y-4">
          {/* Nombre */}
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Nombre completo <span className="text-error-500">*</span>
            </label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Nombre y apellidos..."
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>

          {/* Teléfono / Email */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Teléfono
              </label>
              <input
                type="tel"
                value={contactPhone}
                onChange={(e) => setContactPhone(e.target.value)}
                placeholder="8888-8888"
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Correo
              </label>
              <input
                type="email"
                value={contactEmail}
                onChange={(e) => setContactEmail(e.target.value)}
                placeholder="correo@ejemplo.com"
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
              />
            </div>
          </div>

          {/* Fecha solicitud / Refiere */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Fecha de solicitud
              </label>
              <input
                type="date"
                value={requestedAt}
                onChange={(e) => setRequestedAt(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
                Referido por
              </label>
              <input
                type="text"
                value={referredBy}
                onChange={(e) => setReferredBy(e.target.value)}
                placeholder="Nombre del referente..."
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
              />
            </div>
          </div>

          {/* Notas */}
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Notas
            </label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Observaciones..."
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>
        </div>

        <div className="mt-5 flex justify-end gap-3">
          <Button variant="outline" size="sm" onClick={onCancel} disabled={loading}>
            Cancelar
          </Button>
          <Button
            size="sm"
            onClick={handleSubmit}
            disabled={loading || !fullName.trim()}
          >
            {loading ? "Guardando..." : "Agregar"}
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─── Modal: Editar capacidad ─────────────────────────────────────────────────

interface EditCapacityModalProps {
  current: number;
  onConfirm: (capacity: number) => Promise<void>;
  onCancel: () => void;
  loading: boolean;
}

function EditCapacityModal({ current, onConfirm, onCancel, loading }: EditCapacityModalProps) {
  const [value, setValue] = useState(String(current));
  const parsed = parseInt(value, 10);
  const isValid = !isNaN(parsed) && parsed > 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl dark:bg-gray-900">
        <h3 className="mb-1 text-base font-semibold text-gray-800 dark:text-white">
          Editar capacidad
        </h3>
        <p className="mb-4 text-sm text-gray-500">
          Ingresá la capacidad máxima de camas del centro.
        </p>
        <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Capacidad total <span className="text-error-500">*</span>
        </label>
        <input
          type="number"
          min={1}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="mb-5 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
        />
        <div className="flex justify-end gap-3">
          <Button variant="outline" size="sm" onClick={onCancel} disabled={loading}>
            Cancelar
          </Button>
          <Button
            size="sm"
            onClick={() => onConfirm(parsed)}
            disabled={loading || !isValid}
          >
            {loading ? "Guardando..." : "Guardar"}
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─── Página principal ─────────────────────────────────────────────────────────

const WAITLIST_STATUS_OPTIONS: WaitlistStatus[] = [
  "waiting",
  "admitted",
  "declined",
  "cancelled",
];

export default function OccupancyPage() {
  const [occupancy, setOccupancy] = useState<OccupancyOut | null>(null);
  const [waitlist, setWaitlist] = useState<WaitlistEntryOut[]>([]);
  const [statusFilter, setStatusFilter] = useState<WaitlistStatus | "">("");
  const [loadingOccupancy, setLoadingOccupancy] = useState(false);
  const [loadingWaitlist, setLoadingWaitlist] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [addLoading, setAddLoading] = useState(false);
  const [showCapacityModal, setShowCapacityModal] = useState(false);
  const [capacityLoading, setCapacityLoading] = useState(false);

  // Status action loading per row
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);

  // ── Load occupancy ──────────────────────────────────────────────────────
  const loadOccupancy = useCallback(() => {
    setLoadingOccupancy(true);
    apiFetch<OccupancyOut>("/occupancy")
      .then(setOccupancy)
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Error al cargar ocupación");
      })
      .finally(() => setLoadingOccupancy(false));
  }, []);

  // ── Load waitlist ────────────────────────────────────────────────────────
  const loadWaitlist = useCallback(() => {
    setLoadingWaitlist(true);
    const qs = new URLSearchParams();
    if (statusFilter) qs.set("status", statusFilter);
    apiFetch<WaitlistEntryOut[]>(`/waitlist${qs.toString() ? "?" + qs.toString() : ""}`)
      .then(setWaitlist)
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Error al cargar lista de espera");
      })
      .finally(() => setLoadingWaitlist(false));
  }, [statusFilter]);

  useEffect(() => {
    loadOccupancy();
  }, [loadOccupancy]);

  useEffect(() => {
    loadWaitlist();
  }, [loadWaitlist]);

  // ── Add to waitlist ──────────────────────────────────────────────────────
  async function handleAddWaitlist(data: WaitlistEntryCreate) {
    setAddLoading(true);
    setError(null);
    try {
      await apiFetch<WaitlistEntryOut>("/waitlist", {
        method: "POST",
        body: JSON.stringify(data),
      });
      setShowAddModal(false);
      loadWaitlist();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al agregar entrada");
    } finally {
      setAddLoading(false);
    }
  }

  // ── Update waitlist status ────────────────────────────────────────────────
  async function handleStatusChange(id: number, status: WaitlistStatus) {
    setActionLoadingId(id);
    setError(null);
    const patch: WaitlistEntryPatch = { status };
    try {
      await apiFetch<WaitlistEntryOut>(`/waitlist/${id}`, {
        method: "PATCH",
        body: JSON.stringify(patch),
      });
      // Update admitted status also refreshes occupancy count
      loadWaitlist();
      if (status === "admitted") loadOccupancy();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al cambiar estado");
    } finally {
      setActionLoadingId(null);
    }
  }

  // ── Update capacity ───────────────────────────────────────────────────────
  async function handleSaveCapacity(capacity: number) {
    setCapacityLoading(true);
    setError(null);
    try {
      const result = await apiFetch<CapacityOut>("/settings/capacity", {
        method: "PUT",
        body: JSON.stringify({ capacity }),
      });
      setShowCapacityModal(false);
      // Update occupancy with new capacity
      setOccupancy((prev) =>
        prev
          ? {
              ...prev,
              capacity: result.capacity,
              available: result.capacity - prev.occupied,
            }
          : null
      );
      loadOccupancy();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al actualizar capacidad");
    } finally {
      setCapacityLoading(false);
    }
  }

  const ratio =
    occupancy && occupancy.capacity > 0
      ? occupancy.occupied / occupancy.capacity
      : 0;

  const pct = Math.min(Math.round(ratio * 100), 100);

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Ocupación" />

      {error && (
        <p role="alert" className="text-sm text-error-500">
          {error}
        </p>
      )}

      {/* ── Tablero de cupos ──────────────────────────────────────────────── */}
      <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-white">
            Estado de cupos
          </h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowCapacityModal(true)}
          >
            Editar capacidad
          </Button>
        </div>

        {loadingOccupancy ? (
          <div className="py-6 text-center text-sm text-gray-400">
            Cargando...
          </div>
        ) : occupancy ? (
          <>
            {/* Cards */}
            <div className="mb-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div className="rounded-xl border border-gray-200 p-4 text-center dark:border-gray-700">
                <p className="text-3xl font-bold text-gray-800 dark:text-white">
                  {occupancy.capacity}
                </p>
                <p className="mt-1 text-xs text-gray-500">Capacidad total</p>
              </div>
              <div className="rounded-xl border border-gray-200 p-4 text-center dark:border-gray-700">
                <p className={`text-3xl font-bold ${occupancyTextColor(ratio)}`}>
                  {occupancy.occupied}
                </p>
                <p className="mt-1 text-xs text-gray-500">Ocupadas</p>
              </div>
              <div className="rounded-xl border border-success-200 bg-success-50 p-4 text-center dark:border-success-500/30 dark:bg-success-500/10">
                <p className="text-3xl font-bold text-success-700 dark:text-success-400">
                  {occupancy.available}
                </p>
                <p className="mt-1 text-xs text-success-600 dark:text-success-400">
                  Disponibles
                </p>
              </div>
              <div
                className={`rounded-xl border p-4 text-center ${
                  pct >= 90
                    ? "border-error-200 bg-error-50 dark:border-error-500/30 dark:bg-error-500/10"
                    : pct >= 70
                    ? "border-warning-200 bg-warning-50 dark:border-warning-500/30 dark:bg-warning-500/10"
                    : "border-success-200 bg-success-50 dark:border-success-500/30 dark:bg-success-500/10"
                }`}
              >
                <p
                  className={`text-3xl font-bold ${occupancyTextColor(ratio)}`}
                >
                  {pct}%
                </p>
                <p className={`mt-1 text-xs ${occupancyTextColor(ratio)}`}>
                  Ocupación
                </p>
              </div>
            </div>

            {/* Barra de ocupación */}
            <div className="mb-4">
              <div className="mb-1 flex justify-between text-xs text-gray-500">
                <span>0</span>
                <span>{occupancy.capacity} camas</span>
              </div>
              <div className="h-3 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${occupancyColor(ratio)}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>

            {/* Desglose by_status */}
            {Object.keys(occupancy.by_status).length > 0 && (
              <div className="flex flex-wrap gap-2">
                {Object.entries(occupancy.by_status).map(([key, count]) => (
                  <span
                    key={key}
                    className="inline-flex items-center gap-1.5 rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs font-medium text-gray-600 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-300"
                  >
                    <span className="font-bold text-gray-800 dark:text-white">
                      {count}
                    </span>
                    {STATUS_KEY_LABELS[key] ?? key}
                  </span>
                ))}
              </div>
            )}
          </>
        ) : null}
      </div>

      {/* ── Lista de espera ───────────────────────────────────────────────── */}
      <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 bg-gray-50 px-5 py-4 dark:border-gray-800 dark:bg-gray-800/50">
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="text-sm font-semibold text-gray-700 dark:text-white">
              Lista de espera
            </h2>
            {/* Filtro por estado */}
            <select
              value={statusFilter}
              onChange={(e) =>
                setStatusFilter(e.target.value as WaitlistStatus | "")
              }
              className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            >
              <option value="">Todos los estados</option>
              {WAITLIST_STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>
                  {WAITLIST_STATUS_LABELS[s]}
                </option>
              ))}
            </select>
          </div>
          <Button size="sm" onClick={() => setShowAddModal(true)}>
            + Agregar a lista de espera
          </Button>
        </div>

        {/* Tabla */}
        {loadingWaitlist ? (
          <div className="py-12 text-center text-sm text-gray-400">
            Cargando lista de espera...
          </div>
        ) : waitlist.length === 0 ? (
          <div className="px-5 py-12 text-center text-sm text-gray-400">
            No hay entradas en la lista de espera
            {statusFilter
              ? ` con estado "${WAITLIST_STATUS_LABELS[statusFilter]}"`
              : ""}
            .
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-800">
              <thead className="bg-gray-50/50 dark:bg-gray-800/30">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Nombre
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Contacto
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Solicitud
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Refiere
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Estado
                  </th>
                  <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-gray-500">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {waitlist.map((entry) => {
                  const isLoading = actionLoadingId === entry.id;
                  return (
                    <tr
                      key={entry.id}
                      className="hover:bg-gray-50 dark:hover:bg-white/[0.02]"
                    >
                      {/* Nombre */}
                      <td className="px-4 py-3">
                        <span className="block text-sm font-medium text-gray-800 dark:text-white">
                          {entry.full_name}
                        </span>
                        {entry.notes && (
                          <span className="mt-0.5 block max-w-xs truncate text-xs text-gray-400">
                            {entry.notes}
                          </span>
                        )}
                      </td>

                      {/* Contacto */}
                      <td className="px-4 py-3">
                        {entry.contact_phone && (
                          <span className="block text-sm text-gray-600 dark:text-gray-300">
                            {entry.contact_phone}
                          </span>
                        )}
                        {entry.contact_email && (
                          <span className="block text-xs text-gray-400">
                            {entry.contact_email}
                          </span>
                        )}
                        {!entry.contact_phone && !entry.contact_email && (
                          <span className="text-sm text-gray-300">—</span>
                        )}
                      </td>

                      {/* Fecha */}
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {fmtDate(entry.requested_at)}
                      </td>

                      {/* Refiere */}
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {entry.referred_by ?? "—"}
                      </td>

                      {/* Estado */}
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${WAITLIST_STATUS_BADGE[entry.status]}`}
                        >
                          {WAITLIST_STATUS_LABELS[entry.status]}
                        </span>
                      </td>

                      {/* Acciones */}
                      <td className="px-4 py-3">
                        {entry.status === "waiting" && (
                          <div className="flex flex-wrap gap-1.5 justify-end">
                            <button
                              type="button"
                              disabled={isLoading}
                              onClick={() =>
                                handleStatusChange(entry.id, "admitted")
                              }
                              className="rounded-lg border border-success-300 bg-success-50 px-2.5 py-1 text-xs font-medium text-success-700 transition-colors hover:bg-success-100 disabled:opacity-50 dark:border-success-500/40 dark:bg-success-500/10 dark:text-success-400"
                            >
                              Admitir
                            </button>
                            <button
                              type="button"
                              disabled={isLoading}
                              onClick={() =>
                                handleStatusChange(entry.id, "declined")
                              }
                              className="rounded-lg border border-error-300 bg-error-50 px-2.5 py-1 text-xs font-medium text-error-700 transition-colors hover:bg-error-100 disabled:opacity-50 dark:border-error-500/40 dark:bg-error-500/10 dark:text-error-400"
                            >
                              Rechazar
                            </button>
                            <button
                              type="button"
                              disabled={isLoading}
                              onClick={() =>
                                handleStatusChange(entry.id, "cancelled")
                              }
                              className="rounded-lg border border-gray-300 bg-gray-50 px-2.5 py-1 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-100 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400"
                            >
                              Cancelar
                            </button>
                          </div>
                        )}
                        {entry.status !== "waiting" && (
                          <div className="flex justify-end">
                            <button
                              type="button"
                              disabled={isLoading}
                              onClick={() =>
                                handleStatusChange(entry.id, "waiting")
                              }
                              className="rounded-lg border border-warning-300 bg-warning-50 px-2.5 py-1 text-xs font-medium text-warning-700 transition-colors hover:bg-warning-100 disabled:opacity-50 dark:border-warning-500/40 dark:bg-warning-500/10 dark:text-warning-400"
                            >
                              Volver a espera
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Modals ──────────────────────────────────────────────────────────── */}
      {showAddModal && (
        <AddWaitlistModal
          onConfirm={handleAddWaitlist}
          onCancel={() => setShowAddModal(false)}
          loading={addLoading}
        />
      )}

      {showCapacityModal && occupancy && (
        <EditCapacityModal
          current={occupancy.capacity}
          onConfirm={handleSaveCapacity}
          onCancel={() => setShowCapacityModal(false)}
          loading={capacityLoading}
        />
      )}
    </div>
  );
}
