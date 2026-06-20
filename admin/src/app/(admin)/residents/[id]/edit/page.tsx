"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import type { ResidentOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import ResidentForm from "@/components/residents/ResidentForm";

export default function EditResidentPage() {
  const { id } = useParams<{ id: string }>();
  const [resident, setResident] = useState<ResidentOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    apiFetch<ResidentOut>(`/residents/${id}`)
      .then(setResident)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="p-6 text-sm text-gray-400">Cargando...</div>;
  if (error || !resident) return <div className="p-6 text-sm text-error-500">Residente no encontrado.</div>;

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6">
      <PageBreadcrumb pageTitle={`Editar: ${resident.first_name} ${resident.last_name}`} />
      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 className="mb-6 text-lg font-semibold text-gray-800 dark:text-white">
          Datos del residente
        </h2>
        <ResidentForm initialData={resident} residentId={Number(id)} />
      </div>
    </div>
  );
}
