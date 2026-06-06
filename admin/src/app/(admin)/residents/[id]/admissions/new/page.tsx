"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Input from "@/components/form/input/InputField";
import Label from "@/components/form/Label";
import Button from "@/components/ui/button/Button";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import { apiFetch, ApiError } from "@/lib/api";
import type { AdmissionCreate, AdmissionOut } from "@/types";

export default function NewAdmissionPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [form, setForm] = useState<Omit<AdmissionCreate, "resident_id">>({
    admission_type: "first",
    admission_date: new Date().toISOString().split("T")[0],
    referral_source: "",
    sponsor_name: "",
    sponsor_phone: "",
    has_support_network: false,
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function set(field: keyof typeof form, value: string | boolean) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await apiFetch<AdmissionOut>("/admissions", {
        method: "POST",
        body: JSON.stringify({ ...form, resident_id: Number(id) }),
      });
      router.push(`/residents/${id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al crear admisión");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6">
      <PageBreadcrumb pageTitle="Nueva Admisión" />
      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 className="mb-6 text-lg font-semibold text-gray-800 dark:text-white">Datos de admisión</h2>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <div>
              <Label>Fecha de admisión <span className="text-error-500">*</span></Label>
              <Input type="date" value={form.admission_date} onChange={(e) => set("admission_date", e.target.value)} required />
            </div>
            <div>
              <Label>Tipo</Label>
              <select
                value={form.admission_type}
                onChange={(e) => set("admission_type", e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-700 dark:border-gray-700 dark:bg-gray-900 dark:text-white"
              >
                <option value="first">Primera vez</option>
                <option value="readmission">Reingreso</option>
              </select>
            </div>
            <div>
              <Label>Referido por</Label>
              <Input value={form.referral_source ?? ""} onChange={(e) => set("referral_source", e.target.value)} placeholder="Nombre o institución" />
            </div>
            <div>
              <Label>Nombre del patrocinador</Label>
              <Input value={form.sponsor_name ?? ""} onChange={(e) => set("sponsor_name", e.target.value)} placeholder="Nombre completo" />
            </div>
            <div>
              <Label>Teléfono del patrocinador</Label>
              <Input value={form.sponsor_phone ?? ""} onChange={(e) => set("sponsor_phone", e.target.value)} placeholder="8888-8888" />
            </div>
          </div>

          {error && <p role="alert" className="text-sm text-error-500">{error}</p>}

          <div className="flex gap-3">
            <Button type="button" variant="outline" onClick={() => router.back()} disabled={loading}>Cancelar</Button>
            <Button type="submit" disabled={loading}>{loading ? "Guardando..." : "Crear admisión"}</Button>
          </div>
        </form>
      </div>
    </div>
  );
}
