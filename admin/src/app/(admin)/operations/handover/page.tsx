"use client";

import { useEffect, useState, useCallback } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import type {
  Shift,
  HandoverStatus,
  IncidentSeverity,
  ShiftHandoverOut,
  ShiftIncidentOut,
  ShiftTaskOut,
  UserAdminOut,
} from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

// ─── Helpers & labels ─────────────────────────────────────────────────────────

function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

function fmtDateTime(s: string | null): string {
  if (!s) return "—";
  return new Date(s).toLocaleString("es-CR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const SHIFT_LABELS: Record<Shift, string> = {
  morning: "Mañana",
  afternoon: "Tarde",
  night: "Noche",
};

const STATUS_LABELS: Record<HandoverStatus, string> = {
  open: "Abierto",
  closed: "Cerrado",
  received: "Recibido",
};

const STATUS_BADGE: Record<HandoverStatus, string> = {
  open: "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400",
  closed: "bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400",
  received: "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400",
};

const SEVERITY_LABELS: Record<IncidentSeverity, string> = {
  low: "Baja",
  medium: "Media",
  high: "Alta",
};

const SEVERITY_BADGE: Record<IncidentSeverity, string> = {
  low: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  medium: "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400",
  high: "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400",
};

const MED_STATUS_LABELS: Record<string, string> = {
  omitted: "Omitida",
  refused: "Rechazada",
};

const PRESENCE_LABELS: Record<string, string> = {
  present: "Presente",
  on_pass: "En permiso",
  external_appointment: "Cita externa",
  hospitalized: "Hospitalizado",
  absent_without_leave: "Ausente sin permiso",
  discharged: "Egresado",
};

// ─── Modales ──────────────────────────────────────────────────────────────────

function IncidentModal({
  onConfirm,
  onCancel,
  loading,
}: {
  onConfirm: (data: { type: string; severity: IncidentSeverity; description: string; action_taken: string }) => void;
  onCancel: () => void;
  loading: boolean;
}) {
  const [type, setType] = useState("");
  const [severity, setSeverity] = useState<IncidentSeverity>("medium");
  const [description, setDescription] = useState("");
  const [actionTaken, setActionTaken] = useState("");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-gray-900">
        <h3 className="mb-4 text-base font-semibold text-gray-800 dark:text-white">Nuevo incidente</h3>

        <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Tipo</label>
        <input
          value={type}
          onChange={(e) => setType(e.target.value)}
          placeholder="Ej. conducta, médico, conflicto..."
          className="mb-3 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
        />

        <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Severidad</label>
        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value as IncidentSeverity)}
          className="mb-3 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
        >
          {(["low", "medium", "high"] as IncidentSeverity[]).map((s) => (
            <option key={s} value={s}>
              {SEVERITY_LABELS[s]}
            </option>
          ))}
        </select>

        <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Descripción</label>
        <textarea
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="mb-3 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
        />

        <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Acción tomada <span className="font-normal text-gray-400">(opcional)</span>
        </label>
        <textarea
          rows={2}
          value={actionTaken}
          onChange={(e) => setActionTaken(e.target.value)}
          className="mb-4 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
        />

        <div className="flex justify-end gap-3">
          <Button variant="outline" size="sm" onClick={onCancel} disabled={loading}>
            Cancelar
          </Button>
          <Button
            size="sm"
            disabled={loading || !type.trim() || !description.trim()}
            onClick={() => onConfirm({ type, severity, description, action_taken: actionTaken })}
          >
            {loading ? "Guardando..." : "Agregar incidente"}
          </Button>
        </div>
      </div>
    </div>
  );
}

function TaskModal({
  onConfirm,
  onCancel,
  loading,
}: {
  onConfirm: (data: { description: string; due_at: string | null }) => void;
  onCancel: () => void;
  loading: boolean;
}) {
  const [description, setDescription] = useState("");
  const [dueAt, setDueAt] = useState("");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-gray-900">
        <h3 className="mb-4 text-base font-semibold text-gray-800 dark:text-white">Nuevo pendiente</h3>

        <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Descripción</label>
        <textarea
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="mb-3 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
        />

        <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Vence <span className="font-normal text-gray-400">(opcional)</span>
        </label>
        <input
          type="datetime-local"
          value={dueAt}
          onChange={(e) => setDueAt(e.target.value)}
          className="mb-4 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
        />

        <div className="flex justify-end gap-3">
          <Button variant="outline" size="sm" onClick={onCancel} disabled={loading}>
            Cancelar
          </Button>
          <Button
            size="sm"
            disabled={loading || !description.trim()}
            onClick={() => onConfirm({ description, due_at: dueAt ? new Date(dueAt).toISOString() : null })}
          >
            {loading ? "Guardando..." : "Agregar pendiente"}
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─── Sección del auto-resumen ──────────────────────────────────────────────────

function SummarySection({
  title,
  count,
  children,
}: {
  title: string;
  count: number;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-white/[0.03]">
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-sm font-semibold text-gray-700 dark:text-white">{title}</h4>
        <span className="inline-flex min-w-6 items-center justify-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-400">
          {count}
        </span>
      </div>
      {count === 0 ? (
        <p className="text-sm text-gray-400">Sin novedades</p>
      ) : (
        <ul className="space-y-1.5 text-sm text-gray-600 dark:text-gray-300">{children}</ul>
      )}
    </div>
  );
}

// ─── Página principal ─────────────────────────────────────────────────────────

export default function HandoverPage() {
  const [date, setDate] = useState(todayISO());
  const [shift, setShift] = useState<Shift>("morning");
  const [handover, setHandover] = useState<ShiftHandoverOut | null>(null);
  const [incidents, setIncidents] = useState<ShiftIncidentOut[]>([]);
  const [tasks, setTasks] = useState<ShiftTaskOut[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showIncidentModal, setShowIncidentModal] = useState(false);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [userNames, setUserNames] = useState<Record<number, string>>({});

  useEffect(() => {
    apiFetch<UserAdminOut[]>("/users/")
      .then((users) => setUserNames(Object.fromEntries(users.map((u) => [u.id, u.full_name]))))
      .catch(() => {
        /* selector de nombres opcional: si falla, se muestran los IDs */
      });
  }, []);

  const nameOf = (id: number | null) => (id != null ? userNames[id] ?? `usuario #${id}` : "—");

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    const qs = new URLSearchParams({ date, shift });
    apiFetch<ShiftHandoverOut>(`/shift-handovers?${qs}`)
      .then(async (h) => {
        setHandover(h);
        const [inc, tsk] = await Promise.all([
          apiFetch<ShiftIncidentOut[]>(`/shift-handovers/${h.id}/incidents`),
          apiFetch<ShiftTaskOut[]>(`/shift-handovers/${h.id}/tasks`),
        ]);
        setIncidents(inc);
        setTasks(tsk);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Error al cargar la entrega"))
      .finally(() => setLoading(false));
  }, [date, shift]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleClose() {
    if (!handover) return;
    setActionLoading(true);
    setError(null);
    try {
      const updated = await apiFetch<ShiftHandoverOut>(`/shift-handovers/${handover.id}/close`, {
        method: "POST",
        body: JSON.stringify({}),
      });
      setHandover(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al cerrar el turno");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleReceive() {
    if (!handover) return;
    setActionLoading(true);
    setError(null);
    try {
      const updated = await apiFetch<ShiftHandoverOut>(`/shift-handovers/${handover.id}/receive`, {
        method: "POST",
        body: JSON.stringify({}),
      });
      setHandover(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al recibir el turno");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleAddIncident(data: {
    type: string;
    severity: IncidentSeverity;
    description: string;
    action_taken: string;
  }) {
    if (!handover) return;
    setModalLoading(true);
    try {
      const created = await apiFetch<ShiftIncidentOut>(`/shift-handovers/${handover.id}/incidents`, {
        method: "POST",
        body: JSON.stringify({
          type: data.type,
          severity: data.severity,
          description: data.description,
          action_taken: data.action_taken || null,
        }),
      });
      setIncidents((prev) => [...prev, created]);
      setShowIncidentModal(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al agregar el incidente");
    } finally {
      setModalLoading(false);
    }
  }

  async function handleAddTask(data: { description: string; due_at: string | null }) {
    if (!handover) return;
    setModalLoading(true);
    try {
      const created = await apiFetch<ShiftTaskOut>(`/shift-handovers/${handover.id}/tasks`, {
        method: "POST",
        body: JSON.stringify(data),
      });
      setTasks((prev) => [...prev, created]);
      setShowTaskModal(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al agregar el pendiente");
    } finally {
      setModalLoading(false);
    }
  }

  async function toggleTask(task: ShiftTaskOut) {
    try {
      const updated = await apiFetch<ShiftTaskOut>(`/shift-tasks/${task.id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_done: !task.is_done }),
      });
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al actualizar el pendiente");
    }
  }

  const summary = handover?.auto_summary;
  const status = handover?.status;

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Entrega de turno" />

      {/* ── Filtros ──────────────────────────────────────────────────────── */}
      <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="mb-1 block text-xs font-medium uppercase tracking-wider text-gray-500">Fecha</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium uppercase tracking-wider text-gray-500">Turno</label>
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
          {status && (
            <div className="ml-auto flex items-center gap-3">
              <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${STATUS_BADGE[status]}`}>
                {STATUS_LABELS[status]}
              </span>
              {status === "open" && (
                <Button size="sm" onClick={handleClose} disabled={actionLoading}>
                  {actionLoading ? "..." : "Cerrar turno"}
                </Button>
              )}
              {status === "closed" && (
                <Button size="sm" onClick={handleReceive} disabled={actionLoading}>
                  {actionLoading ? "..." : "Recibir turno"}
                </Button>
              )}
            </div>
          )}
        </div>

        {/* Trazabilidad del apretón de manos */}
        {handover && (status === "closed" || status === "received") && (
          <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-xs text-gray-500">
            <span>
              Cerrado por {nameOf(handover.closed_by_user_id)} · {fmtDateTime(handover.closed_at)}
            </span>
            {status === "received" && (
              <span>
                Recibido por {nameOf(handover.received_by_user_id)} · {fmtDateTime(handover.received_at)}
              </span>
            )}
          </div>
        )}
      </div>

      {error && (
        <p role="alert" className="text-sm text-error-500">
          {error}
        </p>
      )}

      {loading ? (
        <div className="py-12 text-center text-sm text-gray-400">Cargando entrega...</div>
      ) : !summary ? (
        <div className="rounded-xl border border-gray-200 bg-white p-8 text-center text-sm text-gray-400 dark:border-gray-800 dark:bg-white/[0.03]">
          Sin datos para este turno.
        </div>
      ) : (
        <>
          {/* ── Auto-resumen ───────────────────────────────────────────────── */}
          <div>
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-500">
              Resumen automático del turno
              {status === "open" && <span className="ml-2 font-normal normal-case text-gray-400">(en vivo)</span>}
            </h3>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <SummarySection title="Medicamentos (omitidas / rechazadas)" count={summary.medications.length}>
                {summary.medications.map((m) => (
                  <li key={m.administration_id} className="flex items-center justify-between">
                    <span>Admisión #{m.admission_id}</span>
                    <span className="text-error-600 dark:text-error-400">{MED_STATUS_LABELS[m.status] ?? m.status}</span>
                  </li>
                ))}
              </SummarySection>

              <SummarySection title="Asistencia (ausencias / discrepancias)" count={summary.attendance.length}>
                {summary.attendance.map((a) => (
                  <li key={a.entry_id} className="flex items-center justify-between">
                    <span>Admisión #{a.admission_id}</span>
                    <span>
                      {PRESENCE_LABELS[a.expected_status] ?? a.expected_status} →{" "}
                      <span className="font-medium text-gray-800 dark:text-white">
                        {PRESENCE_LABELS[a.actual_status] ?? a.actual_status}
                      </span>
                    </span>
                  </li>
                ))}
              </SummarySection>

              <SummarySection title="Permisos (salidas / retornos)" count={summary.exit_passes.length}>
                {summary.exit_passes.map((p) => (
                  <li key={p.exit_pass_id} className="flex items-center justify-between">
                    <span>Admisión #{p.admission_id}</span>
                    <span>{p.events.map((e) => (e === "departure" ? "Salida" : "Retorno")).join(" + ")}</span>
                  </li>
                ))}
              </SummarySection>

              <SummarySection title="Ingresos del día" count={summary.admissions.length}>
                {summary.admissions.map((a) => (
                  <li key={a.admission_id}>
                    {a.admission_number} (Admisión #{a.admission_id})
                  </li>
                ))}
              </SummarySection>
            </div>
          </div>

          {/* ── Incidentes ─────────────────────────────────────────────────── */}
          <div className="rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3 dark:border-gray-800">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-white">Incidentes</h3>
              <Button size="sm" variant="outline" onClick={() => setShowIncidentModal(true)}>
                Agregar incidente
              </Button>
            </div>
            {incidents.length === 0 ? (
              <p className="px-4 py-6 text-center text-sm text-gray-400">Sin incidentes registrados.</p>
            ) : (
              <ul className="divide-y divide-gray-100 dark:divide-gray-800">
                {incidents.map((i) => (
                  <li key={i.id} className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${SEVERITY_BADGE[i.severity]}`}>
                        {SEVERITY_LABELS[i.severity]}
                      </span>
                      <span className="text-sm font-medium text-gray-800 dark:text-white">{i.type}</span>
                      {i.admission_id && <span className="text-xs text-gray-400">· Admisión #{i.admission_id}</span>}
                    </div>
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{i.description}</p>
                    {i.action_taken && (
                      <p className="mt-0.5 text-xs text-gray-400">Acción: {i.action_taken}</p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* ── Pendientes ─────────────────────────────────────────────────── */}
          <div className="rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
            <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3 dark:border-gray-800">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-white">Pendientes para el siguiente turno</h3>
              <Button size="sm" variant="outline" onClick={() => setShowTaskModal(true)}>
                Agregar pendiente
              </Button>
            </div>
            {tasks.length === 0 ? (
              <p className="px-4 py-6 text-center text-sm text-gray-400">Sin pendientes.</p>
            ) : (
              <ul className="divide-y divide-gray-100 dark:divide-gray-800">
                {tasks.map((t) => (
                  <li key={t.id} className="flex items-start gap-3 px-4 py-3">
                    <input
                      type="checkbox"
                      checked={t.is_done}
                      onChange={() => toggleTask(t)}
                      className="mt-0.5 h-4 w-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
                    />
                    <div className="flex-1">
                      <p className={`text-sm ${t.is_done ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-200"}`}>
                        {t.description}
                      </p>
                      {t.due_at && <p className="mt-0.5 text-xs text-gray-400">Vence: {fmtDateTime(t.due_at)}</p>}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}

      {showIncidentModal && (
        <IncidentModal
          loading={modalLoading}
          onCancel={() => setShowIncidentModal(false)}
          onConfirm={handleAddIncident}
        />
      )}
      {showTaskModal && (
        <TaskModal loading={modalLoading} onCancel={() => setShowTaskModal(false)} onConfirm={handleAddTask} />
      )}
    </div>
  );
}
