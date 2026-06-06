"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { ResidentList } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

export default function ResidentsPage() {
  const [residents, setResidents] = useState<ResidentList[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = query ? `?q=${encodeURIComponent(query)}` : "";
    apiFetch<ResidentList[]>(`/residents${params}`)
      .then(setResidents)
      .finally(() => setLoading(false));
  }, [query]);

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6">
      <PageBreadcrumb pageTitle="Residentes" />

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-4">
        <input
          type="search"
          placeholder="Buscar por nombre o cédula..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full sm:w-72 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
        />
        <Link href="/residents/new">
          <Button size="sm">+ Nuevo residente</Button>
        </Link>
      </div>

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-800">
            <thead className="bg-gray-50 dark:bg-gray-800/50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Código</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Nombre</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Cédula</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Teléfono</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Fecha ingreso</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {loading && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-sm text-gray-400">Cargando...</td>
                </tr>
              )}
              {!loading && residents.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-sm text-gray-400">
                    {query ? "Sin resultados para la búsqueda." : "Aún no hay residentes registrados."}
                  </td>
                </tr>
              )}
              {residents.map((r) => (
                <tr key={r.id} className="hover:bg-gray-50 dark:hover:bg-white/[0.02]">
                  <td className="px-4 py-3 text-sm font-mono text-gray-500">{r.code}</td>
                  <td className="px-4 py-3 text-sm font-medium text-gray-800 dark:text-white">
                    {r.first_name} {r.last_name}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">{r.id_number ?? "—"}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{r.phone_mobile ?? "—"}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {new Date(r.created_at).toLocaleDateString("es-CR")}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link href={`/residents/${r.id}`} className="text-sm text-brand-500 hover:underline">
                      Ver
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
