"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiFetch, ApiError } from "@/lib/api";
import type {
  AccountOut,
  AgreementType,
  ChargeCreate,
  ChargeOut,
  PayerType,
  PaymentAgreementOut,
  PaymentAgreementUpsert,
  PaymentCreate,
  PaymentMethod,
  PaymentOut,
} from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";

// ─── Labels ──────────────────────────────────────────────────────────────────

const AGREEMENT_LABELS: Record<AgreementType, string> = {
  monthly: "Mensualidad",
  fixed_total: "Monto fijo total",
  scholarship_full: "Beca total",
  scholarship_partial: "Beca parcial",
};

const METHOD_LABELS: Record<PaymentMethod, string> = {
  cash: "Efectivo",
  sinpe: "SINPE Móvil",
  transfer: "Transferencia",
  check: "Cheque",
  other: "Otro",
};

const PAYER_LABELS: Record<PayerType, string> = {
  family: "Familia / Responsable",
  iafa: "IAFA",
  imas: "IMAS",
  church: "Iglesia",
  donor: "Donante",
  other: "Otro",
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

function fmtCRC(amount: number): string {
  return "₡" + new Intl.NumberFormat("es-CR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

function fmtDate(iso: string): string {
  return new Date(iso + "T12:00:00").toLocaleDateString("es-CR", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03] space-y-4">
      <h3 className="text-base font-semibold text-gray-800 dark:text-white">{title}</h3>
      {children}
    </div>
  );
}

// ─── Agreement Form ───────────────────────────────────────────────────────────

interface AgreementFormProps {
  initial: PaymentAgreementOut | null;
  onSave: (data: PaymentAgreementUpsert) => Promise<void>;
  onCancel: () => void;
}

function AgreementForm({ initial, onSave, onCancel }: AgreementFormProps) {
  const [type, setType] = useState<AgreementType>(initial?.agreement_type ?? "monthly");
  const [amount, setAmount] = useState(initial ? String(initial.amount) : "");
  const [billingDay, setBillingDay] = useState(initial?.billing_day ? String(initial.billing_day) : "1");
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSave() {
    const parsed = parseFloat(amount.replace(/,/g, "."));
    if (!amount || isNaN(parsed) || parsed <= 0) { setError("Ingrese un monto válido mayor a 0."); return; }
    setSaving(true); setError(null);
    try {
      await onSave({
        agreement_type: type,
        amount: parsed,
        billing_day: type === "monthly" ? (parseInt(billingDay) || 1) : null,
        notes: notes.trim() || null,
        is_active: true,
      });
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-3">
      {error && <p className="text-sm text-error-500">{error}</p>}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500">Tipo de acuerdo</label>
          <select
            value={type}
            onChange={(e) => setType(e.target.value as AgreementType)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          >
            {(Object.entries(AGREEMENT_LABELS) as [AgreementType, string][]).map(([v, l]) => (
              <option key={v} value={v}>{l}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500">
            Monto (₡) <span className="text-error-500">*</span>
          </label>
          <input
            type="number"
            min="0"
            step="1000"
            placeholder="500000"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>
        {type === "monthly" && (
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500">Día de cobro del mes</label>
            <input
              type="number"
              min="1"
              max="28"
              value={billingDay}
              onChange={(e) => setBillingDay(e.target.value)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>
        )}
        <div className={type === "monthly" ? "" : "sm:col-span-2"}>
          <label className="mb-1 block text-xs font-medium text-gray-500">Notas</label>
          <input
            type="text"
            placeholder="Observaciones del acuerdo..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>
      </div>
      <div className="flex justify-end gap-2">
        <Button variant="outline" size="sm" onClick={onCancel} disabled={saving}>Cancelar</Button>
        <Button size="sm" onClick={handleSave} disabled={saving}>
          {saving ? "Guardando..." : "Guardar acuerdo"}
        </Button>
      </div>
    </div>
  );
}

// ─── Charge Form ──────────────────────────────────────────────────────────────

interface ChargeFormProps {
  onSave: (data: ChargeCreate) => Promise<void>;
  onCancel: () => void;
}

function ChargeForm({ onSave, onCancel }: ChargeFormProps) {
  const [concept, setConcept] = useState("");
  const [amount, setAmount] = useState("");
  const [chargeDate, setChargeDate] = useState(today());
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSave() {
    if (!concept.trim()) { setError("El concepto es requerido."); return; }
    const parsed = parseFloat(amount.replace(/,/g, "."));
    if (!amount || isNaN(parsed) || parsed <= 0) { setError("Ingrese un monto válido mayor a 0."); return; }
    setSaving(true); setError(null);
    try {
      await onSave({ concept: concept.trim(), amount: parsed, charge_date: chargeDate, notes: notes.trim() || null });
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mt-4 rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/40 space-y-3">
      {error && <p className="text-sm text-error-500">{error}</p>}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div className="sm:col-span-2">
          <label className="mb-1 block text-xs font-medium text-gray-500">Concepto <span className="text-error-500">*</span></label>
          <input
            type="text"
            placeholder="Ej: Depósito de ingreso"
            value={concept}
            onChange={(e) => setConcept(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500">Monto (₡) <span className="text-error-500">*</span></label>
          <input
            type="number"
            min="0"
            step="1000"
            placeholder="100000"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500">Fecha</label>
          <input
            type="date"
            value={chargeDate}
            onChange={(e) => setChargeDate(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>
        <div className="sm:col-span-2">
          <label className="mb-1 block text-xs font-medium text-gray-500">Notas</label>
          <input
            type="text"
            placeholder="Observaciones..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>
      </div>
      <div className="flex justify-end gap-2">
        <Button variant="outline" size="sm" onClick={onCancel} disabled={saving}>Cancelar</Button>
        <Button size="sm" onClick={handleSave} disabled={saving}>{saving ? "Guardando..." : "Agregar cargo"}</Button>
      </div>
    </div>
  );
}

// ─── Payment Form ─────────────────────────────────────────────────────────────

interface PaymentFormProps {
  onSave: (data: PaymentCreate) => Promise<void>;
  onCancel: () => void;
}

function PaymentForm({ onSave, onCancel }: PaymentFormProps) {
  const [amount, setAmount] = useState("");
  const [paymentDate, setPaymentDate] = useState(today());
  const [method, setMethod] = useState<PaymentMethod>("sinpe");
  const [payerType, setPayerType] = useState<PayerType>("family");
  const [payerName, setPayerName] = useState("");
  const [reference, setReference] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSave() {
    const parsed = parseFloat(amount.replace(/,/g, "."));
    if (!amount || isNaN(parsed) || parsed <= 0) { setError("Ingrese un monto válido mayor a 0."); return; }
    setSaving(true); setError(null);
    try {
      await onSave({
        amount: parsed,
        payment_date: paymentDate,
        method,
        payer_type: payerType,
        payer_name: payerName.trim() || null,
        reference: reference.trim() || null,
        notes: notes.trim() || null,
      });
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mt-4 rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/40 space-y-3">
      {error && <p className="text-sm text-error-500">{error}</p>}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500">Monto (₡) <span className="text-error-500">*</span></label>
          <input
            type="number"
            min="0"
            step="1000"
            placeholder="100000"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500">Fecha de pago</label>
          <input
            type="date"
            value={paymentDate}
            onChange={(e) => setPaymentDate(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500">Método</label>
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value as PaymentMethod)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          >
            {(Object.entries(METHOD_LABELS) as [PaymentMethod, string][]).map(([v, l]) => (
              <option key={v} value={v}>{l}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500">Tipo de pagador</label>
          <select
            value={payerType}
            onChange={(e) => setPayerType(e.target.value as PayerType)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          >
            {(Object.entries(PAYER_LABELS) as [PayerType, string][]).map(([v, l]) => (
              <option key={v} value={v}>{l}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500">Nombre del pagador</label>
          <input
            type="text"
            placeholder="Ej: María López"
            value={payerName}
            onChange={(e) => setPayerName(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-500">Referencia / # SINPE</label>
          <input
            type="text"
            placeholder="Número de transacción"
            value={reference}
            onChange={(e) => setReference(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>
        <div className="sm:col-span-3">
          <label className="mb-1 block text-xs font-medium text-gray-500">Notas</label>
          <input
            type="text"
            placeholder="Observaciones..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>
      </div>
      <div className="flex justify-end gap-2">
        <Button variant="outline" size="sm" onClick={onCancel} disabled={saving}>Cancelar</Button>
        <Button size="sm" onClick={handleSave} disabled={saving}>{saving ? "Registrando..." : "Registrar pago"}</Button>
      </div>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function AdmissionFinancePage() {
  const { id } = useParams<{ id: string }>();
  const [account, setAccount] = useState<AccountOut | null>(null);
  const [agreement, setAgreement] = useState<PaymentAgreementOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showAgreementForm, setShowAgreementForm] = useState(false);
  const [showChargeForm, setShowChargeForm] = useState(false);
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [deletingCharge, setDeletingCharge] = useState<number | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [acc, agr] = await Promise.allSettled([
        apiFetch<AccountOut>(`/admissions/${id}/account`),
        apiFetch<PaymentAgreementOut>(`/admissions/${id}/payment-agreement`),
      ]);
      if (acc.status === "fulfilled") setAccount(acc.value);
      if (agr.status === "fulfilled") setAgreement(agr.value);
      else setAgreement(null);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Error al cargar");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [id]);

  async function handleSaveAgreement(data: PaymentAgreementUpsert) {
    await apiFetch<PaymentAgreementOut>(`/admissions/${id}/payment-agreement`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
    setShowAgreementForm(false);
    await load();
  }

  async function handleAddCharge(data: ChargeCreate) {
    await apiFetch<ChargeOut>(`/admissions/${id}/charges`, {
      method: "POST",
      body: JSON.stringify(data),
    });
    setShowChargeForm(false);
    await load();
  }

  async function handleDeleteCharge(chargeId: number) {
    setDeletingCharge(chargeId);
    try {
      await apiFetch(`/charges/${chargeId}`, { method: "DELETE" });
      await load();
    } finally {
      setDeletingCharge(null);
    }
  }

  async function handleAddPayment(data: PaymentCreate) {
    await apiFetch<PaymentOut>(`/admissions/${id}/payments`, {
      method: "POST",
      body: JSON.stringify(data),
    });
    setShowPaymentForm(false);
    await load();
  }

  if (loading) return <div className="p-6 text-sm text-gray-400">Cargando...</div>;

  const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "/api/v1";
  const balance = account?.balance ?? 0;
  const balanceColor =
    balance > 0
      ? "text-error-700 dark:text-error-400"
      : balance < 0
      ? "text-success-700 dark:text-success-400"
      : "text-gray-700 dark:text-white";

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Link href={`/admissions/${id}`} className="text-sm text-gray-400 hover:text-brand-500">
          ← Volver a la admisión
        </Link>
      </div>
      <PageBreadcrumb pageTitle="Control financiero" />

      {error && <p className="text-sm text-error-500">{error}</p>}

      {/* Balance */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-gray-400 mb-1">Saldo pendiente (+ = debe, − = a favor)</p>
            <p className={`text-4xl font-bold ${balanceColor}`}>{fmtCRC(balance)}</p>
            {balance < 0 && (
              <p className="mt-1 text-xs text-gray-400">Saldo a favor del residente.</p>
            )}
          </div>
          <a
            href={`${API_BASE}/admissions/${id}/account/statement`}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-800"
          >
            Estado de cuenta PDF
          </a>
        </div>
      </div>

      {/* Acuerdo de pago */}
      <SectionCard title="Acuerdo de pago">
        {!showAgreementForm ? (
          <>
            {agreement ? (
              <div className="flex items-start justify-between">
                <dl className="text-sm space-y-1">
                  <div className="flex gap-4">
                    <dt className="text-gray-400 w-28">Tipo</dt>
                    <dd className="text-gray-700 dark:text-white">{AGREEMENT_LABELS[agreement.agreement_type]}</dd>
                  </div>
                  <div className="flex gap-4">
                    <dt className="text-gray-400 w-28">Monto</dt>
                    <dd className="font-semibold text-gray-800 dark:text-white">{fmtCRC(agreement.amount)}</dd>
                  </div>
                  {agreement.agreement_type === "monthly" && agreement.billing_day && (
                    <div className="flex gap-4">
                      <dt className="text-gray-400 w-28">Día de cobro</dt>
                      <dd className="text-gray-700 dark:text-white">Día {agreement.billing_day}</dd>
                    </div>
                  )}
                  {agreement.notes && (
                    <div className="flex gap-4">
                      <dt className="text-gray-400 w-28">Notas</dt>
                      <dd className="text-gray-500">{agreement.notes}</dd>
                    </div>
                  )}
                </dl>
                <Button variant="outline" size="sm" onClick={() => setShowAgreementForm(true)}>
                  Editar
                </Button>
              </div>
            ) : (
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-400">Sin acuerdo de pago registrado.</p>
                <Button size="sm" onClick={() => setShowAgreementForm(true)}>+ Crear acuerdo</Button>
              </div>
            )}
          </>
        ) : (
          <AgreementForm
            initial={agreement}
            onSave={handleSaveAgreement}
            onCancel={() => setShowAgreementForm(false)}
          />
        )}
      </SectionCard>

      {/* Cargos */}
      <SectionCard title="Cargos">
        {account && account.charges.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-800 text-sm">
              <thead>
                <tr className="text-left text-xs uppercase text-gray-400">
                  <th className="py-2 pr-4">Concepto</th>
                  <th className="py-2 pr-4">Fecha</th>
                  <th className="py-2 pr-4 text-right">Monto</th>
                  <th className="py-2 pr-4">Periodo</th>
                  <th />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                {account.charges.map((c: ChargeOut) => (
                  <tr key={c.id}>
                    <td className="py-2 pr-4 text-gray-700 dark:text-white">
                      {c.concept}
                      {c.is_auto && (
                        <span className="ml-2 text-xs text-gray-400">(auto)</span>
                      )}
                    </td>
                    <td className="py-2 pr-4 text-gray-500">{fmtDate(c.charge_date)}</td>
                    <td className="py-2 pr-4 text-right font-mono text-gray-700 dark:text-white">
                      {fmtCRC(c.amount)}
                    </td>
                    <td className="py-2 pr-4 text-gray-400">{c.period ?? "—"}</td>
                    <td className="py-2 text-right">
                      <button
                        onClick={() => handleDeleteCharge(c.id)}
                        disabled={deletingCharge === c.id}
                        className="text-xs text-error-500 hover:underline disabled:opacity-50"
                      >
                        {deletingCharge === c.id ? "..." : "Eliminar"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-gray-400">Sin cargos registrados.</p>
        )}

        {!showChargeForm ? (
          <div className="pt-2">
            <Button variant="outline" size="sm" onClick={() => setShowChargeForm(true)}>
              + Agregar cargo manual
            </Button>
          </div>
        ) : (
          <ChargeForm onSave={handleAddCharge} onCancel={() => setShowChargeForm(false)} />
        )}
      </SectionCard>

      {/* Pagos */}
      <SectionCard title="Pagos recibidos">
        {account && account.payments.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-800 text-sm">
              <thead>
                <tr className="text-left text-xs uppercase text-gray-400">
                  <th className="py-2 pr-4">Recibo #</th>
                  <th className="py-2 pr-4">Fecha</th>
                  <th className="py-2 pr-4">Pagador</th>
                  <th className="py-2 pr-4">Método</th>
                  <th className="py-2 pr-4">Referencia</th>
                  <th className="py-2 pr-4 text-right">Monto</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                {account.payments.map((p: PaymentOut) => (
                  <tr key={p.id}>
                    <td className="py-2 pr-4 font-mono text-gray-500">
                      <a
                        href={`${API_BASE}/payments/${p.id}/receipt`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:underline text-brand-500"
                        title="Descargar recibo PDF"
                      >
                        #{p.receipt_number}
                      </a>
                    </td>
                    <td className="py-2 pr-4 text-gray-500">{fmtDate(p.payment_date)}</td>
                    <td className="py-2 pr-4 text-gray-700 dark:text-white">
                      {PAYER_LABELS[p.payer_type]}
                      {p.payer_name && <span className="block text-xs text-gray-400">{p.payer_name}</span>}
                    </td>
                    <td className="py-2 pr-4 text-gray-500">{METHOD_LABELS[p.method]}</td>
                    <td className="py-2 pr-4 text-gray-400">{p.reference ?? "—"}</td>
                    <td className="py-2 pr-4 text-right font-mono font-semibold text-success-700 dark:text-success-400">
                      {fmtCRC(p.amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-gray-400">Sin pagos registrados.</p>
        )}

        {!showPaymentForm ? (
          <div className="pt-2">
            <Button size="sm" onClick={() => setShowPaymentForm(true)}>
              + Registrar pago
            </Button>
          </div>
        ) : (
          <PaymentForm onSave={handleAddPayment} onCancel={() => setShowPaymentForm(false)} />
        )}
      </SectionCard>
    </div>
  );
}
