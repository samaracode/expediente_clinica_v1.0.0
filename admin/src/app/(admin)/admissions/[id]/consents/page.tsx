"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type { ConsentItem, ConsentType } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

const CONSENT_LABELS: Record<ConsentType, string> = {
  INTERNMENT_SERVICE: "Consentimiento de servicio de internamiento",
  INTERNMENT: "Consentimiento de internamiento",
  SEARCH: "Autorización de registro personal",
  DRUG_TEST: "Consentimiento para prueba de drogas",
  CCTV: "Consentimiento de vigilancia CCTV",
  INFO_RELEASE: "Autorización de divulgación de información",
  WEAPONS: "Declaración de armas y objetos peligrosos",
  IAFA_ACTIONS: "Consentimiento de acciones IAFA",
  INDIVIDUAL_APPROACH: "Consentimiento de abordaje individual",
  REFERRAL: "Consentimiento de referencia",
  RECORD_ACCESS: "Autorización de acceso al expediente",
  RIGHTS_FOCUS: "Declaración de enfoque de derechos",
  LABOR: "Consentimiento laboral",
  NON_DISCRIMINATION: "Política de no discriminación",
  SPONSOR: "Consentimiento del patrocinador",
  MANUAL: "Aceptación del manual del residente",
  LABOR_PROVISION: "Consentimiento de provisión laboral",
};

interface SignModalProps {
  consentType: ConsentType;
  onConfirm: (notes: string) => void;
  onCancel: () => void;
  loading: boolean;
}

function SignModal({ consentType, onConfirm, onCancel, loading }: SignModalProps) {
  const [notes, setNotes] = useState("");
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-gray-900">
        <h3 className="mb-1 text-base font-semibold text-gray-800 dark:text-white">
          Registrar firma
        </h3>
        <p className="mb-4 text-sm text-gray-500">{CONSENT_LABELS[consentType]}</p>

        <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
          Observaciones <span className="text-gray-400 font-normal">(opcional)</span>
        </label>
        <textarea
          rows={3}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Notas adicionales sobre la firma..."
          className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
        />

        <div className="mt-4 flex justify-end gap-3">
          <Button variant="outline" size="sm" onClick={onCancel} disabled={loading}>
            Cancelar
          </Button>
          <Button size="sm" onClick={() => onConfirm(notes)} disabled={loading}>
            {loading ? "Guardando..." : "Confirmar firma"}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default function ConsentsPage() {
  const { id } = useParams<{ id: string }>();
  const [consents, setConsents] = useState<ConsentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [signing, setSigning] = useState<ConsentType | null>(null);
  const [signLoading, setSignLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<ConsentItem[]>(`/admissions/${id}/consents`)
      .then(setConsents)
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSign(consentType: ConsentType, notes: string) {
    setSignLoading(true);
    setError(null);
    try {
      const updated = await apiFetch<ConsentItem>(
        `/admissions/${id}/consents/${consentType}/sign`,
        { method: "POST", body: JSON.stringify({ notes: notes || null }) }
      );
      setConsents((prev) =>
        prev.map((c) => (c.consent_type === consentType ? updated : c))
      );
      setSigning(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al registrar firma");
    } finally {
      setSignLoading(false);
    }
  }

  const signedCount = consents.filter((c) => c.is_signed).length;
  const total = consents.length;
  const allSigned = total > 0 && signedCount === total;

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Consentimientos" />

      {/* Header con progreso */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
              Consentimientos informados
            </h2>
            <p className="text-sm text-gray-500">
              <Link href={`/admissions/${id}`} className="text-brand-500 hover:underline">
                Admisión #{id}
              </Link>
            </p>
          </div>

          <div className="flex flex-col items-end gap-1">
            <p className="text-sm font-medium text-gray-700 dark:text-white">
              {signedCount} de {total} firmados
            </p>
            <div className="h-2 w-48 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
              <div
                className={`h-full rounded-full transition-all ${allSigned ? "bg-success-500" : "bg-brand-500"}`}
                style={{ width: total > 0 ? `${(signedCount / total) * 100}%` : "0%" }}
              />
            </div>
          </div>
        </div>

        {allSigned && (
          <div className="mt-4 rounded-lg bg-success-50 px-4 py-3 text-sm text-success-700 dark:bg-success-500/10 dark:text-success-400">
            Todos los consentimientos han sido firmados.
          </div>
        )}
      </div>

      {error && (
        <p role="alert" className="text-sm text-error-500">{error}</p>
      )}

      {/* Tabla */}
      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
        {loading ? (
          <div className="px-4 py-8 text-center text-sm text-gray-400">Cargando...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-800">
              <thead className="bg-gray-50 dark:bg-gray-800/50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Consentimiento
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Estado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Fecha de firma
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Observaciones
                  </th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {consents.map((c) => (
                  <tr key={c.consent_type} className="hover:bg-gray-50 dark:hover:bg-white/[0.02]">
                    <td className="px-4 py-3 text-sm text-gray-700 dark:text-white">
                      {CONSENT_LABELS[c.consent_type]}
                    </td>
                    <td className="px-4 py-3">
                      {c.is_signed ? (
                        <span className="inline-flex items-center rounded-full bg-success-50 px-2.5 py-0.5 text-xs font-medium text-success-700 dark:bg-success-500/10 dark:text-success-400">
                          Firmado
                        </span>
                      ) : (
                        <span className="inline-flex items-center rounded-full bg-warning-50 px-2.5 py-0.5 text-xs font-medium text-warning-700 dark:bg-warning-500/10 dark:text-warning-400">
                          Pendiente
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {c.signed_at
                        ? new Date(c.signed_at).toLocaleDateString("es-CR", {
                            day: "2-digit",
                            month: "2-digit",
                            year: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })
                        : "—"}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-400 max-w-xs truncate">
                      {c.notes ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {!c.is_signed && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setSigning(c.consent_type)}
                        >
                          Registrar firma
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {signing && (
        <SignModal
          consentType={signing}
          onConfirm={(notes) => handleSign(signing, notes)}
          onCancel={() => setSigning(null)}
          loading={signLoading}
        />
      )}
    </div>
  );
}
