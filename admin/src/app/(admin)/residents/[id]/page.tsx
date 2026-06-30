"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type { AdmissionOut, ResidentOut, ResidentAllergyOut, ResidentAllergyCreate, AllergySeverity } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";
import AdmissionStatusBadge from "@/components/residents/AdmissionStatusBadge";
import { useAuth } from "@/context/AuthContext";

const SEVERITY_LABELS: Record<AllergySeverity, string> = {
  mild: "Leve",
  moderate: "Moderada",
  severe: "Severa",
};

const SEVERITY_BADGE: Record<AllergySeverity, string> = {
  mild: "bg-warning-50 text-warning-700 dark:bg-warning-500/10 dark:text-warning-400",
  moderate: "bg-orange-50 text-orange-700 dark:bg-orange-500/10 dark:text-orange-400",
  severe: "bg-error-50 text-error-700 dark:bg-error-500/10 dark:text-error-400",
};

export default function ResidentProfilePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const [resident, setResident] = useState<ResidentOut | null>(null);
  const [admissions, setAdmissions] = useState<AdmissionOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirmArchive, setConfirmArchive] = useState(false);
  const [archiving, setArchiving] = useState(false);

  // Alergias
  const [allergies, setAllergies] = useState<ResidentAllergyOut[]>([]);
  const [allergyError, setAllergyError] = useState<string | null>(null);
  const [showAllergyForm, setShowAllergyForm] = useState(false);
  const [newSubstance, setNewSubstance] = useState("");
  const [newReaction, setNewReaction] = useState("");
  const [newSeverity, setNewSeverity] = useState<AllergySeverity | "">("");
  const [savingAllergy, setSavingAllergy] = useState(false);
  const [deletingAllergyId, setDeletingAllergyId] = useState<number | null>(null);

  useEffect(() => {
    Promise.all([
      apiFetch<ResidentOut>(`/residents/${id}`),
      apiFetch<AdmissionOut[]>(`/admissions/resident/${id}`),
    ])
      .then(([r, a]) => { setResident(r); setAdmissions(a); })
      .finally(() => setLoading(false));

    apiFetch<ResidentAllergyOut[]>(`/residents/${id}/allergies`)
      .then(setAllergies)
      .catch(() => {});
  }, [id]);

  async function handleAddAllergy() {
    if (!newSubstance.trim()) return;
    setSavingAllergy(true);
    setAllergyError(null);
    try {
      const payload: ResidentAllergyCreate = {
        substance: newSubstance,
        reaction: newReaction || undefined,
        severity: newSeverity || undefined,
      };
      const created = await apiFetch<ResidentAllergyOut>(
        `/residents/${id}/allergies`,
        { method: "POST", body: JSON.stringify(payload) }
      );
      setAllergies((prev) => [...prev, created]);
      setNewSubstance("");
      setNewReaction("");
      setNewSeverity("");
      setShowAllergyForm(false);
    } catch (err) {
      setAllergyError(err instanceof ApiError ? err.message : "Error al guardar");
    } finally {
      setSavingAllergy(false);
    }
  }

  async function handleDeleteAllergy(allergyId: number) {
    setDeletingAllergyId(allergyId);
    try {
      await apiFetch(`/residents/${id}/allergies/${allergyId}`, { method: "DELETE" });
      setAllergies((prev) => prev.filter((a) => a.id !== allergyId));
    } catch (err) {
      setAllergyError(err instanceof ApiError ? err.message : "Error al eliminar");
    } finally {
      setDeletingAllergyId(null);
    }
  }

  async function handleArchive() {
    setArchiving(true);
    try {
      await apiFetch(`/residents/${id}`, { method: "DELETE" });
      router.push("/residents");
    } finally {
      setArchiving(false);
    }
  }

  if (loading) return <div className="p-6 text-sm text-gray-400">Cargando...</div>;
  if (!resident) return <div className="p-6 text-sm text-error-500">Residente no encontrado.</div>;

  const age = resident.birthdate
    ? Math.floor((Date.now() - new Date(resident.birthdate).getTime()) / (365.25 * 24 * 3600 * 1000))
    : null;

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle={`${resident.first_name} ${resident.last_name}`} />

      {/* Datos del residente */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-xs font-mono text-gray-400">{resident.code}</p>
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white">
              {resident.first_name} {resident.last_name}
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <Link href={`/residents/${id}/relatives`}>
              <Button variant="outline" size="sm">Familiares</Button>
            </Link>
            <Link href={`/residents/${id}/edit`}>
              <Button variant="outline" size="sm">Editar</Button>
            </Link>
            {user?.role === "admin" && !resident.is_deleted && (
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
                <Button variant="outline" size="sm" onClick={() => setConfirmArchive(true)}>
                  Archivar
                </Button>
              )
            )}
          </div>
        </div>
        <dl className="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-3 text-sm">
          <div><dt className="text-gray-400">Cédula</dt><dd className="text-gray-700 dark:text-white">{resident.id_number ?? "—"}</dd></div>
          <div><dt className="text-gray-400">Edad</dt><dd className="text-gray-700 dark:text-white">{age != null ? `${age} años` : "—"}</dd></div>
          <div><dt className="text-gray-400">Teléfono</dt><dd className="text-gray-700 dark:text-white">{resident.phone_mobile ?? "—"}</dd></div>
          <div><dt className="text-gray-400">Provincia</dt><dd className="text-gray-700 dark:text-white">{resident.province ?? "—"}</dd></div>
          <div><dt className="text-gray-400">Contacto emergencia</dt><dd className="text-gray-700 dark:text-white">{resident.emergency_contact_name ?? "—"}</dd></div>
          <div><dt className="text-gray-400">Tel. emergencia</dt><dd className="text-gray-700 dark:text-white">{resident.emergency_contact_phone ?? "—"}</dd></div>
        </dl>
      </div>

      {/* Historial de admisiones */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-gray-800 dark:text-white">Admisiones</h3>
          <Link href={`/residents/${id}/admissions/new`}>
            <Button size="sm">+ Nueva admisión</Button>
          </Link>
        </div>

        {admissions.length === 0 ? (
          <p className="text-sm text-gray-400">Sin admisiones registradas.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-800 text-sm">
              <thead>
                <tr className="text-left text-xs uppercase text-gray-400">
                  <th className="py-2 pr-4">Número</th>
                  <th className="py-2 pr-4">Fecha</th>
                  <th className="py-2 pr-4">Tipo</th>
                  <th className="py-2 pr-4">Estado</th>
                  <th />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                {admissions.map((a) => (
                  <tr key={a.id}>
                    <td className="py-2 pr-4 font-mono text-gray-500">{a.admission_number}</td>
                    <td className="py-2 pr-4 text-gray-700 dark:text-white">
                      {new Date(a.admission_date).toLocaleDateString("es-CR")}
                    </td>
                    <td className="py-2 pr-4 text-gray-500">
                      {a.admission_type === "first" ? "Primera vez" : "Reingreso"}
                    </td>
                    <td className="py-2 pr-4">
                      <AdmissionStatusBadge status={a.status} />
                    </td>
                    <td className="py-2 text-right">
                      <Link href={`/admissions/${a.id}`} className="text-brand-500 hover:underline">Ver</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Alergias */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-gray-800 dark:text-white">Alergias</h3>
          {!showAllergyForm && (
            <Button size="sm" variant="outline" onClick={() => setShowAllergyForm(true)}>
              + Agregar alergia
            </Button>
          )}
        </div>

        {allergyError && (
          <p className="mb-3 text-sm text-error-500">{allergyError}</p>
        )}

        {allergies.length === 0 && !showAllergyForm ? (
          <p className="text-sm text-gray-400">Sin alergias registradas.</p>
        ) : (
          <div className="space-y-2">
            {allergies.map((allergy) => (
              <div
                key={allergy.id}
                className="flex items-center justify-between rounded-lg border border-gray-100 px-4 py-3 dark:border-gray-800"
              >
                <div>
                  <span className="text-sm font-medium text-gray-800 dark:text-white">
                    {allergy.substance}
                  </span>
                  {allergy.reaction && (
                    <span className="ml-2 text-sm text-gray-500">— {allergy.reaction}</span>
                  )}
                  {allergy.severity && (
                    <span
                      className={`ml-2 inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${SEVERITY_BADGE[allergy.severity]}`}
                    >
                      {SEVERITY_LABELS[allergy.severity]}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => handleDeleteAllergy(allergy.id)}
                  disabled={deletingAllergyId === allergy.id}
                  className="ml-4 text-xs text-error-500 hover:underline disabled:opacity-50"
                >
                  {deletingAllergyId === allergy.id ? "Eliminando..." : "Eliminar"}
                </button>
              </div>
            ))}
          </div>
        )}

        {showAllergyForm && (
          <div className="mt-4 rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/40 space-y-3">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-500">
                  Sustancia <span className="text-error-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="Ej: Penicilina"
                  value={newSubstance}
                  onChange={(e) => setNewSubstance(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-500">
                  Reacción
                </label>
                <input
                  type="text"
                  placeholder="Ej: urticaria, anafilaxia"
                  value={newReaction}
                  onChange={(e) => setNewReaction(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-500">
                  Severidad
                </label>
                <select
                  value={newSeverity}
                  onChange={(e) => setNewSeverity(e.target.value as AllergySeverity | "")}
                  className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                >
                  <option value="">Sin especificar</option>
                  <option value="mild">Leve</option>
                  <option value="moderate">Moderada</option>
                  <option value="severe">Severa</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setShowAllergyForm(false);
                  setNewSubstance("");
                  setNewReaction("");
                  setNewSeverity("");
                  setAllergyError(null);
                }}
                disabled={savingAllergy}
              >
                Cancelar
              </Button>
              <Button
                size="sm"
                onClick={handleAddAllergy}
                disabled={savingAllergy || !newSubstance.trim()}
              >
                {savingAllergy ? "Guardando..." : "Guardar alergia"}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
