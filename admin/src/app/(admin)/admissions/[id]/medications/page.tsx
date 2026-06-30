"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, apiFetchMultipart, ApiError } from "@/lib/api";
import type {
  MedicationOrderOut,
  MedicationOut,
  MedTimeSlotOut,
  MedicationCreate,
  MedicationOrderCreate,
  MedicationAdministrationOut,
  FileUploadOut,
  OrderStatus,
  MedicationRoute,
  ScheduleType,
  UserAdminOut,
} from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

// ─── Helpers ────────────────────────────────────────────────────────────────

const STATUS_LABELS: Record<OrderStatus, string> = {
  active: "Activa",
  suspended: "Suspendida",
  finished: "Finalizada",
};

const STATUS_BADGE: Record<OrderStatus, string> = {
  active: "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400",
  suspended:
    "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400",
  finished: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
};

const ADMIN_STATUS_BADGE: Record<string, string> = {
  pending: "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400",
  taken: "bg-success-50 text-success-700 dark:bg-success-500/10 dark:text-success-400",
  refused: "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400",
  omitted: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
};

const ADMIN_STATUS_LABELS: Record<string, string> = {
  pending: "Pendiente",
  taken: "Administrado",
  refused: "Rechazado",
  omitted: "Omitido",
};

const ROUTE_OPTIONS: { value: MedicationRoute; label: string }[] = [
  { value: "oral", label: "Oral" },
  { value: "IM", label: "IM (intramuscular)" },
  { value: "SC", label: "SC (subcutánea)" },
  { value: "otra", label: "Otra" },
];

// ─── Modal de suspender / finalizar ─────────────────────────────────────────

interface PatchModalProps {
  order: MedicationOrderOut;
  action: "suspended" | "finished";
  onConfirm: () => void;
  onCancel: () => void;
  loading: boolean;
}

function PatchModal({ order, action, onConfirm, onCancel, loading }: PatchModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl dark:bg-gray-900">
        <h3 className="mb-2 text-base font-semibold text-gray-800 dark:text-white">
          {action === "suspended" ? "Suspender orden" : "Finalizar orden"}
        </h3>
        <p className="mb-5 text-sm text-gray-500">
          ¿Confirmar que deseas {action === "suspended" ? "suspender" : "finalizar"} la orden de{" "}
          <span className="font-medium text-gray-700 dark:text-white">
            {order.medication_id}
          </span>
          ?
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="outline" size="sm" onClick={onCancel} disabled={loading}>
            Cancelar
          </Button>
          <Button size="sm" onClick={onConfirm} disabled={loading}>
            {loading ? "Guardando..." : "Confirmar"}
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─── Modal de historial de tomas ─────────────────────────────────────────────

interface HistoryModalProps {
  orderId: number;
  onClose: () => void;
}

function HistoryModal({ orderId, onClose }: HistoryModalProps) {
  const [administrations, setAdministrations] = useState<MedicationAdministrationOut[]>([]);
  const [userNames, setUserNames] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      apiFetch<MedicationAdministrationOut[]>(`/medication-orders/${orderId}/administrations`),
      apiFetch<UserAdminOut[]>("/users/").catch(() => [] as UserAdminOut[]),
    ])
      .then(([adms, users]) => {
        setAdministrations(adms);
        setUserNames(Object.fromEntries(users.map((u) => [u.id, u.full_name])));
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Error al cargar historial");
      })
      .finally(() => setLoading(false));
  }, [orderId]);

  const nameOf = (id: number | null) => (id != null ? userNames[id] ?? `Usuario #${id}` : null);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl dark:bg-gray-900">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-base font-semibold text-gray-800 dark:text-white">
            Historial de tomas
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            ✕
          </button>
        </div>

        {loading ? (
          <div className="py-6 text-center text-sm text-gray-400">Cargando...</div>
        ) : error ? (
          <div className="rounded-lg bg-error-50 px-3 py-2 text-sm text-error-700 dark:bg-error-500/10 dark:text-error-400">
            {error}
          </div>
        ) : administrations.length === 0 ? (
          <p className="py-4 text-center text-sm text-gray-400">
            No hay tomas registradas para esta orden.
          </p>
        ) : (
          <div className="max-h-[60vh] overflow-y-auto space-y-2">
            {administrations.map((a) => (
              <div
                key={a.id}
                className={`rounded-lg border px-3 py-3 ${
                  a.is_overdue && a.status === "pending"
                    ? "border-error-200 bg-error-50/50 dark:border-error-500/30 dark:bg-error-500/5"
                    : "border-gray-100 dark:border-gray-800"
                }`}
              >
                {/* Primera fila: fecha pautada + estado */}
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm text-gray-700 dark:text-white">
                    {a.scheduled_at
                      ? new Date(a.scheduled_at).toLocaleString("es-CR", {
                          dateStyle: "short",
                          timeStyle: "short",
                        })
                      : "PRN"}
                    {a.is_overdue && a.status === "pending" && (
                      <span className="ml-1 text-error-600 dark:text-error-400">⚠</span>
                    )}
                  </span>
                  <span
                    className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${ADMIN_STATUS_BADGE[a.status] ?? ""}`}
                  >
                    {ADMIN_STATUS_LABELS[a.status] ?? a.status}
                  </span>
                </div>

                {/* Segunda fila: hora real + administrador */}
                {a.administered_at && (
                  <div className="mt-1 flex flex-wrap gap-x-3 text-xs text-gray-500">
                    <span>
                      Administrado:{" "}
                      {new Date(a.administered_at).toLocaleString("es-CR", {
                        dateStyle: "short",
                        timeStyle: "short",
                      })}
                    </span>
                    {a.administered_by_user_id && (
                      <span>Por: {nameOf(a.administered_by_user_id)}</span>
                    )}
                    {a.witness_user_id && (
                      <span>Testigo: {nameOf(a.witness_user_id)}</span>
                    )}
                  </div>
                )}

                {/* Motivo / notas */}
                {(a.reason || a.notes) && (
                  <div className="mt-1 space-y-0.5 text-xs text-gray-400">
                    {a.reason && <p>Motivo: {a.reason}</p>}
                    {a.notes && <p>Notas: {a.notes}</p>}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="mt-4 flex justify-end">
          <Button variant="outline" size="sm" onClick={onClose}>
            Cerrar
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─── Modal de nueva orden ─────────────────────────────────────────────────────

interface NewOrderModalProps {
  admissionId: string;
  slots: MedTimeSlotOut[];
  catalog: MedicationOut[];
  onCreated: (order: MedicationOrderOut) => void;
  onCancel: () => void;
}

function NewOrderModal({
  admissionId,
  slots,
  catalog,
  onCreated,
  onCancel,
}: NewOrderModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Campos del medicamento
  const [medSearch, setMedSearch] = useState("");
  const [selectedMedId, setSelectedMedId] = useState<number | null>(null);
  const [createNewMed, setCreateNewMed] = useState(false);
  const [newMedName, setNewMedName] = useState("");
  const [newMedForm, setNewMedForm] = useState("");
  const [newMedStrength, setNewMedStrength] = useState("");
  const [newMedControlled, setNewMedControlled] = useState(false);

  // Campos de la orden
  const [dose, setDose] = useState("");
  const [route, setRoute] = useState<MedicationRoute>("oral");
  const [scheduleType, setScheduleType] = useState<ScheduleType>("scheduled");
  const [selectedSlots, setSelectedSlots] = useState<string[]>([]);
  const [frequencyText, setFrequencyText] = useState("");
  const [prnReason, setPrnReason] = useState("");
  const [startDate, setStartDate] = useState(new Date().toISOString().slice(0, 10));
  const [endDate, setEndDate] = useState("");
  const [prescribedBy, setPrescribedBy] = useState("");
  const [institution, setInstitution] = useState("");
  const [isControlled, setIsControlled] = useState(false);
  const [notes, setNotes] = useState("");
  const [recetaFile, setRecetaFile] = useState<File | null>(null);

  const filteredCatalog = catalog.filter((m) =>
    m.name.toLowerCase().includes(medSearch.toLowerCase())
  );

  function toggleSlot(slotId: string) {
    setSelectedSlots((prev) =>
      prev.includes(slotId) ? prev.filter((s) => s !== slotId) : [...prev, slotId]
    );
  }

  async function handleSubmit() {
    if (!dose.trim() || !startDate) {
      setError("Dosis y fecha de inicio son obligatorios.");
      return;
    }
    if (!selectedMedId && !createNewMed) {
      setError("Seleccioná o creá un medicamento.");
      return;
    }
    if (createNewMed && !newMedName.trim()) {
      setError("Nombre del medicamento es obligatorio.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 1. Crear medicamento nuevo si se indicó
      let medicationId = selectedMedId;
      if (createNewMed) {
        const newMedPayload: MedicationCreate = {
          name: newMedName,
          form: newMedForm || undefined,
          strength: newMedStrength || undefined,
          is_controlled: newMedControlled,
        };
        const created = await apiFetch<MedicationOut>("/medications", {
          method: "POST",
          body: JSON.stringify(newMedPayload),
        });
        medicationId = created.id;
      }

      // 2. Subir foto de la receta si se adjuntó
      let recetaFileId: number | undefined;
      if (recetaFile) {
        const fd = new FormData();
        fd.append("file", recetaFile);
        fd.append("entity_type", "medication_order");
        const uploaded = await apiFetchMultipart<FileUploadOut>("/files", fd);
        recetaFileId = uploaded.id;
      }

      // 3. Crear la orden
      const orderPayload: MedicationOrderCreate = {
        admission_id: Number(admissionId),
        medication_id: medicationId!,
        dose,
        route,
        schedule_type: scheduleType,
        times:
          scheduleType === "scheduled" && selectedSlots.length > 0
            ? selectedSlots
            : undefined,
        frequency_text: frequencyText || undefined,
        prn_reason: prnReason || undefined,
        start_date: startDate,
        end_date: endDate || undefined,
        prescribed_by_external: prescribedBy || undefined,
        prescriber_institution: institution || undefined,
        is_controlled: isControlled,
        receta_file_id: recetaFileId,
        notes: notes || undefined,
      };

      const order = await apiFetch<MedicationOrderOut>(
        `/admissions/${admissionId}/medication-orders`,
        { method: "POST", body: JSON.stringify(orderPayload) }
      );
      onCreated(order);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al crear la orden");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 py-8">
      <div className="w-full max-w-xl rounded-2xl bg-white p-6 shadow-xl dark:bg-gray-900">
        <h3 className="mb-4 text-base font-semibold text-gray-800 dark:text-white">
          Nueva orden de medicamento
        </h3>

        {error && (
          <div className="mb-4 rounded-lg bg-error-50 px-3 py-2 text-sm text-error-700 dark:bg-error-500/10 dark:text-error-400">
            {error}
          </div>
        )}

        {/* Selección de medicamento */}
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Medicamento <span className="text-error-500">*</span>
          </label>

          {!createNewMed ? (
            <>
              <input
                type="text"
                placeholder="Buscar en catálogo..."
                value={medSearch}
                onChange={(e) => {
                  setMedSearch(e.target.value);
                  setSelectedMedId(null);
                }}
                className="mb-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
              />
              {medSearch && (
                <div className="max-h-40 overflow-y-auto rounded-lg border border-gray-200 bg-white shadow dark:border-gray-700 dark:bg-gray-800">
                  {filteredCatalog.length === 0 ? (
                    <p className="px-3 py-2 text-sm text-gray-400">Sin resultados</p>
                  ) : (
                    filteredCatalog.slice(0, 10).map((m) => (
                      <button
                        key={m.id}
                        type="button"
                        onClick={() => {
                          setSelectedMedId(m.id);
                          setMedSearch(m.name + (m.strength ? ` ${m.strength}` : ""));
                          setIsControlled(m.is_controlled);
                        }}
                        className={`w-full px-3 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700 ${
                          selectedMedId === m.id
                            ? "bg-brand-50 dark:bg-brand-500/10"
                            : ""
                        }`}
                      >
                        {m.name}
                        {m.strength && (
                          <span className="ml-1 text-gray-400">{m.strength}</span>
                        )}
                        {m.is_controlled && (
                          <span className="ml-2 text-xs text-error-600">Controlado</span>
                        )}
                      </button>
                    ))
                  )}
                </div>
              )}
              <button
                type="button"
                onClick={() => setCreateNewMed(true)}
                className="mt-1 text-xs text-brand-500 hover:underline"
              >
                + Crear medicamento nuevo
              </button>
            </>
          ) : (
            <div className="rounded-lg border border-gray-200 p-3 dark:border-gray-700 space-y-2">
              <p className="text-xs font-medium text-gray-500">Nuevo medicamento</p>
              <input
                type="text"
                placeholder="Nombre *"
                value={newMedName}
                onChange={(e) => setNewMedName(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
              />
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Forma (tableta, jarabe...)"
                  value={newMedForm}
                  onChange={(e) => setNewMedForm(e.target.value)}
                  className="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                />
                <input
                  type="text"
                  placeholder="Concentración (50 mg...)"
                  value={newMedStrength}
                  onChange={(e) => setNewMedStrength(e.target.value)}
                  className="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                />
              </div>
              <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                <input
                  type="checkbox"
                  checked={newMedControlled}
                  onChange={(e) => {
                    setNewMedControlled(e.target.checked);
                    setIsControlled(e.target.checked);
                  }}
                />
                Medicamento controlado / psicotrópico
              </label>
              <button
                type="button"
                onClick={() => setCreateNewMed(false)}
                className="text-xs text-gray-400 hover:underline"
              >
                Cancelar (buscar en catálogo)
              </button>
            </div>
          )}
        </div>

        {/* Dosis y vía */}
        <div className="mb-4 grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Dosis <span className="text-error-500">*</span>
            </label>
            <input
              type="text"
              placeholder="Ej: 1 tableta, 50 mg"
              value={dose}
              onChange={(e) => setDose(e.target.value)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Vía
            </label>
            <select
              value={route}
              onChange={(e) => setRoute(e.target.value as MedicationRoute)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            >
              {ROUTE_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Tipo de horario */}
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Tipo
          </label>
          <div className="flex gap-2">
            {(["scheduled", "prn"] as ScheduleType[]).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setScheduleType(t)}
                className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors ${
                  scheduleType === t
                    ? "border-brand-500 bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-400"
                    : "border-gray-300 text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400"
                }`}
              >
                {t === "scheduled" ? "Horario fijo" : "PRN (a demanda)"}
              </button>
            ))}
          </div>
        </div>

        {/* Franjas (si scheduled) */}
        {scheduleType === "scheduled" && slots.length > 0 && (
          <div className="mb-4">
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Franjas horarias
            </label>
            <div className="flex flex-wrap gap-2">
              {slots.map((s) => (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => toggleSlot(String(s.id))}
                  className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
                    selectedSlots.includes(String(s.id))
                      ? "border-brand-500 bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-400"
                      : "border-gray-300 text-gray-500 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400"
                  }`}
                >
                  {s.label} ({s.time.slice(0, 5)})
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Frecuencia texto */}
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Frecuencia (texto de la receta)
          </label>
          <input
            type="text"
            placeholder="Ej: cada 12 horas, tres veces al día..."
            value={frequencyText}
            onChange={(e) => setFrequencyText(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>

        {/* Motivo PRN */}
        {scheduleType === "prn" && (
          <div className="mb-4">
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Indicación PRN
            </label>
            <input
              type="text"
              placeholder="Ej: dolor, insomnio, ansiedad..."
              value={prnReason}
              onChange={(e) => setPrnReason(e.target.value)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>
        )}

        {/* Fechas */}
        <div className="mb-4 grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Fecha inicio <span className="text-error-500">*</span>
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Fecha fin (opcional)
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>
        </div>

        {/* Prescriptor */}
        <div className="mb-4 grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Prescrito por (externo)
            </label>
            <input
              type="text"
              placeholder="Dr. / médico externo"
              value={prescribedBy}
              onChange={(e) => setPrescribedBy(e.target.value)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
              Institución
            </label>
            <input
              type="text"
              placeholder="Hospital / clínica"
              value={institution}
              onChange={(e) => setInstitution(e.target.value)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>
        </div>

        {/* Controlado */}
        <div className="mb-4">
          <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <input
              type="checkbox"
              checked={isControlled}
              onChange={(e) => setIsControlled(e.target.checked)}
            />
            Medicamento controlado / psicotrópico
          </label>
        </div>

        {/* Foto de receta */}
        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Foto de la receta (opcional)
          </label>
          <input
            type="file"
            accept="image/*,application/pdf"
            onChange={(e) => setRecetaFile(e.target.files?.[0] ?? null)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-500 outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400"
          />
          {recetaFile && (
            <p className="mt-1 text-xs text-gray-400">
              {recetaFile.name} ({(recetaFile.size / 1024).toFixed(0)} KB)
            </p>
          )}
        </div>

        {/* Notas */}
        <div className="mb-5">
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Notas
          </label>
          <textarea
            rows={2}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>

        <div className="flex justify-end gap-3">
          <Button variant="outline" size="sm" onClick={onCancel} disabled={loading}>
            Cancelar
          </Button>
          <Button size="sm" onClick={handleSubmit} disabled={loading}>
            {loading ? "Guardando..." : "Crear orden"}
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─── Modal de toma PRN ───────────────────────────────────────────────────────

interface PRNModalProps {
  order: MedicationOrderOut;
  medName: string;
  onConfirm: (reason: string, notes: string) => void;
  onCancel: () => void;
  loading: boolean;
}

function PRNModal({ order, medName, onConfirm, onCancel, loading }: PRNModalProps) {
  const [reason, setReason] = useState("");
  const [notes, setNotes] = useState("");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-gray-900">
        <h3 className="mb-1 text-base font-semibold text-gray-800 dark:text-white">
          Registrar toma PRN
        </h3>
        <p className="mb-4 text-sm text-gray-500">
          <span className="font-medium text-gray-700 dark:text-white">{medName}</span>
          {order.prn_reason && (
            <span className="ml-1 text-gray-400">— {order.prn_reason}</span>
          )}
        </p>

        <div className="mb-4">
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Motivo de administración <span className="text-error-500">*</span>
          </label>
          <textarea
            rows={2}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Ej: dolor agudo, insomnio, crisis de ansiedad..."
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>

        <div className="mb-5">
          <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
            Notas <span className="text-gray-400 font-normal">(opcional)</span>
          </label>
          <textarea
            rows={2}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>

        <div className="flex justify-end gap-3">
          <Button variant="outline" size="sm" onClick={onCancel} disabled={loading}>
            Cancelar
          </Button>
          <Button
            size="sm"
            onClick={() => onConfirm(reason, notes)}
            disabled={loading || !reason.trim()}
          >
            {loading ? "Guardando..." : "Registrar"}
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─── Página principal ────────────────────────────────────────────────────────

export default function AdmissionMedicationsPage() {
  const { id } = useParams<{ id: string }>();
  const [orders, setOrders] = useState<MedicationOrderOut[]>([]);
  const [catalog, setCatalog] = useState<MedicationOut[]>([]);
  const [slots, setSlots] = useState<MedTimeSlotOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showNewOrder, setShowNewOrder] = useState(false);
  const [patchTarget, setPatchTarget] = useState<{
    order: MedicationOrderOut;
    action: "suspended" | "finished";
  } | null>(null);
  const [patchLoading, setPatchLoading] = useState(false);
  const [historyTarget, setHistoryTarget] = useState<number | null>(null);
  const [prnTarget, setPrnTarget] = useState<MedicationOrderOut | null>(null);
  const [prnLoading, setPrnLoading] = useState(false);

  const loadOrders = useCallback(() => {
    setLoading(true);
    apiFetch<MedicationOrderOut[]>(`/admissions/${id}/medication-orders`)
      .then(setOrders)
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Error al cargar órdenes");
      })
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    loadOrders();
    apiFetch<MedicationOut[]>("/medications").then(setCatalog).catch(() => {});
    apiFetch<MedTimeSlotOut[]>("/settings/medication-slots")
      .then(setSlots)
      .catch(() => {});
  }, [loadOrders]);

  async function handlePRN(order: MedicationOrderOut, reason: string, notes: string) {
    setPrnLoading(true);
    setError(null);
    try {
      await apiFetch<MedicationAdministrationOut>(
        `/admissions/${id}/medication-orders/${order.id}/prn`,
        {
          method: "POST",
          body: JSON.stringify({ reason, notes: notes || undefined }),
        }
      );
      setPrnTarget(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al registrar toma PRN");
    } finally {
      setPrnLoading(false);
    }
  }

  async function handlePatch(order: MedicationOrderOut, action: "suspended" | "finished") {
    setPatchLoading(true);
    setError(null);
    try {
      const updated = await apiFetch<MedicationOrderOut>(
        `/medication-orders/${order.id}`,
        {
          method: "PATCH",
          body: JSON.stringify({ status: action }),
        }
      );
      setOrders((prev) => prev.map((o) => (o.id === order.id ? updated : o)));
      setPatchTarget(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al actualizar orden");
    } finally {
      setPatchLoading(false);
    }
  }

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Medicamentos" />

      {/* Header */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
              Órdenes de medicamentos
            </h2>
            <p className="text-sm text-gray-500">
              <Link href={`/admissions/${id}`} className="text-brand-500 hover:underline">
                Admisión #{id}
              </Link>
            </p>
          </div>
          <Button size="sm" onClick={() => setShowNewOrder(true)}>
            + Nueva orden
          </Button>
        </div>
      </div>

      {error && (
        <p role="alert" className="text-sm text-error-500">{error}</p>
      )}

      {/* Tabla de órdenes */}
      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
        {loading ? (
          <div className="px-4 py-8 text-center text-sm text-gray-400">Cargando...</div>
        ) : orders.length === 0 ? (
          <div className="px-4 py-8 text-center text-sm text-gray-400">
            No hay órdenes registradas para esta admisión.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-800">
              <thead className="bg-gray-50 dark:bg-gray-800/50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Medicamento
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Dosis / Vía
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Tipo
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Vigencia
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Estado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Prescriptor
                  </th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {orders.map((order) => {
                  const med = catalog.find((m) => m.id === order.medication_id);
                  return (
                    <tr
                      key={order.id}
                      className="hover:bg-gray-50 dark:hover:bg-white/[0.02]"
                    >
                      <td className="px-4 py-3 text-sm font-medium text-gray-800 dark:text-white">
                        <span>{med?.name ?? `#${order.medication_id}`}</span>
                        {order.is_controlled && (
                          <span className="ml-2 inline-flex items-center rounded-full bg-error-50 px-2 py-0.5 text-xs font-medium text-error-700 dark:bg-error-500/10 dark:text-error-400">
                            Controlado
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {order.dose} — {order.route}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {order.schedule_type === "scheduled" ? "Horario fijo" : "PRN"}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {new Date(order.start_date).toLocaleDateString("es-CR")}
                        {order.end_date
                          ? ` → ${new Date(order.end_date).toLocaleDateString("es-CR")}`
                          : " →"}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_BADGE[order.status]}`}
                        >
                          {STATUS_LABELS[order.status]}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {order.prescribed_by_external ?? "—"}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => setHistoryTarget(order.id)}
                            className="rounded px-2 py-1 text-xs font-medium border border-gray-300 text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400"
                          >
                            Historial
                          </button>
                          {order.status === "active" && (
                            <>
                              {order.schedule_type === "prn" && (
                                <button
                                  onClick={() => setPrnTarget(order)}
                                  className="rounded px-2 py-1 text-xs font-medium border border-brand-300 text-brand-700 hover:bg-brand-50 dark:border-brand-700 dark:text-brand-400"
                                >
                                  Toma PRN
                                </button>
                              )}
                              <button
                                onClick={() =>
                                  setPatchTarget({ order, action: "suspended" })
                                }
                                className="rounded px-2 py-1 text-xs font-medium border border-warning-300 text-warning-700 hover:bg-warning-50 dark:border-warning-700 dark:text-warning-400"
                              >
                                Suspender
                              </button>
                              <button
                                onClick={() =>
                                  setPatchTarget({ order, action: "finished" })
                                }
                                className="rounded px-2 py-1 text-xs font-medium border border-gray-300 text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400"
                              >
                                Finalizar
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showNewOrder && (
        <NewOrderModal
          admissionId={id}
          slots={slots}
          catalog={catalog}
          onCreated={(order) => {
            setOrders((prev) => [order, ...prev]);
            setShowNewOrder(false);
          }}
          onCancel={() => setShowNewOrder(false)}
        />
      )}

      {patchTarget && (
        <PatchModal
          order={patchTarget.order}
          action={patchTarget.action}
          onConfirm={() => handlePatch(patchTarget.order, patchTarget.action)}
          onCancel={() => setPatchTarget(null)}
          loading={patchLoading}
        />
      )}

      {historyTarget !== null && (
        <HistoryModal
          orderId={historyTarget}
          onClose={() => setHistoryTarget(null)}
        />
      )}

      {prnTarget && (
        <PRNModal
          order={prnTarget}
          medName={catalog.find((m) => m.id === prnTarget.medication_id)?.name ?? `#${prnTarget.medication_id}`}
          onConfirm={(reason, notes) => handlePRN(prnTarget, reason, notes)}
          onCancel={() => setPrnTarget(null)}
          loading={prnLoading}
        />
      )}
    </div>
  );
}
