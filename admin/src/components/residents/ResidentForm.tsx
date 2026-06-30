"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Input from "@/components/form/input/InputField";
import Label from "@/components/form/Label";
import Button from "@/components/ui/button/Button";
import { apiFetch, ApiError } from "@/lib/api";
import type { ResidentCreate, ResidentOut } from "@/types";

interface Props {
  initialData?: ResidentOut;
  residentId?: number;
}

export default function ResidentForm({ initialData, residentId }: Props) {
  const router = useRouter();
  const isEdit = !!residentId;

  const [form, setForm] = useState<ResidentCreate>({
    first_name: initialData?.first_name ?? "",
    last_name: initialData?.last_name ?? "",
    id_number: initialData?.id_number ?? "",
    birthdate: initialData?.birthdate ?? "",
    sex: initialData?.sex ?? undefined,
    marital_status: initialData?.marital_status ?? undefined,
    phone_mobile: initialData?.phone_mobile ?? "",
    phone_home: "",
    emergency_contact_name: initialData?.emergency_contact_name ?? "",
    emergency_contact_phone: initialData?.emergency_contact_phone ?? "",
    nationality: initialData?.nationality ?? "Costarricense",
    province: initialData?.province ?? "",
    canton: initialData?.canton ?? "",
    district: initialData?.district ?? "",
    is_insured: initialData?.is_insured ?? false,
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function set(field: keyof ResidentCreate, value: string | boolean) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (isEdit) {
        await apiFetch<ResidentOut>(`/residents/${residentId}`, {
          method: "PUT",
          body: JSON.stringify(form),
        });
        router.push(`/residents/${residentId}`);
      } else {
        const resident = await apiFetch<ResidentOut>("/residents", {
          method: "POST",
          body: JSON.stringify(form),
        });
        router.push(`/residents/${resident.id}`);
      }
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : isEdit
          ? "Error al actualizar residente"
          : "Error al crear residente"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div>
          <Label>Nombre <span className="text-error-500">*</span></Label>
          <Input value={form.first_name} onChange={(e) => set("first_name", e.target.value)} placeholder="Nombre" required />
        </div>
        <div>
          <Label>Apellidos <span className="text-error-500">*</span></Label>
          <Input value={form.last_name} onChange={(e) => set("last_name", e.target.value)} placeholder="Apellidos" required />
        </div>
        <div>
          <Label>Cédula</Label>
          <Input value={form.id_number ?? ""} onChange={(e) => set("id_number", e.target.value)} placeholder="0-0000-0000" />
        </div>
        <div>
          <Label>Fecha de nacimiento</Label>
          <Input type="date" value={form.birthdate ?? ""} onChange={(e) => set("birthdate", e.target.value)} />
        </div>
        <div>
          <Label>Teléfono celular</Label>
          <Input value={form.phone_mobile ?? ""} onChange={(e) => set("phone_mobile", e.target.value)} placeholder="8888-8888" />
        </div>
        <div>
          <Label>Teléfono casa</Label>
          <Input value={form.phone_home ?? ""} onChange={(e) => set("phone_home", e.target.value)} placeholder="2222-2222" />
        </div>
        <div>
          <Label>Contacto de emergencia</Label>
          <Input value={form.emergency_contact_name ?? ""} onChange={(e) => set("emergency_contact_name", e.target.value)} placeholder="Nombre del contacto" />
        </div>
        <div>
          <Label>Teléfono de emergencia</Label>
          <Input value={form.emergency_contact_phone ?? ""} onChange={(e) => set("emergency_contact_phone", e.target.value)} placeholder="8888-8888" />
        </div>
        <div>
          <Label>Provincia</Label>
          <Input value={form.province ?? ""} onChange={(e) => set("province", e.target.value)} placeholder="San José" />
        </div>
        <div>
          <Label>Cantón</Label>
          <Input value={form.canton ?? ""} onChange={(e) => set("canton", e.target.value)} placeholder="San José" />
        </div>
        <div>
          <Label>Distrito</Label>
          <Input value={form.district ?? ""} onChange={(e) => set("district", e.target.value)} placeholder="Carmen" />
        </div>
        <div>
          <Label>Nacionalidad</Label>
          <Input value={form.nationality ?? ""} onChange={(e) => set("nationality", e.target.value)} placeholder="Costarricense" />
        </div>
      </div>

      {error && <p role="alert" className="text-sm text-error-500">{error}</p>}

      <div className="flex gap-3">
        <Button type="button" variant="outline" onClick={() => router.back()} disabled={loading}>
          Cancelar
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? "Guardando..." : isEdit ? "Guardar cambios" : "Crear residente"}
        </Button>
      </div>
    </form>
  );
}
