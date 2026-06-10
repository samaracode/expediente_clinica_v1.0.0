"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { AdmissionOut, ResidentOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";
import AdmissionStatusBadge from "@/components/residents/AdmissionStatusBadge";

export default function ResidentProfilePage() {
  const { id } = useParams<{ id: string }>();
  const [resident, setResident] = useState<ResidentOut | null>(null);
  const [admissions, setAdmissions] = useState<AdmissionOut[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiFetch<ResidentOut>(`/residents/${id}`),
      apiFetch<AdmissionOut[]>(`/admissions/resident/${id}`),
    ])
      .then(([r, a]) => { setResident(r); setAdmissions(a); })
      .finally(() => setLoading(false));
  }, [id]);

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
    </div>
  );
}
