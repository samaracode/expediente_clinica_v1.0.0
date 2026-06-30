"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import type { FinanceOverviewOut, OverdueEntryOut } from "@/types";
import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/button/Button";
import Link from "next/link";

// ─── Labels ──────────────────────────────────────────────────────────────────

const PAYER_LABELS: Record<string, string> = {
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

function currentPeriod(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function periodLabel(period: string): string {
  const [year, month] = period.split("-");
  const d = new Date(Number(year), Number(month) - 1, 1);
  return d.toLocaleDateString("es-CR", { month: "long", year: "numeric" });
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function FinanceDashboardPage() {
  const [period, setPeriod] = useState(currentPeriod);
  const [overview, setOverview] = useState<FinanceOverviewOut | null>(null);
  const [overdue, setOverdue] = useState<OverdueEntryOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [genMsg, setGenMsg] = useState<string | null>(null);

  const load = useCallback(async (p: string) => {
    setLoading(true);
    setError(null);
    try {
      const [ov, od] = await Promise.all([
        apiFetch<FinanceOverviewOut>(`/finance/overview?period=${p}`),
        apiFetch<OverdueEntryOut[]>(`/finance/overdue`),
      ]);
      setOverview(ov);
      setOverdue(od);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Error al cargar");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(period); }, [period, load]);

  async function handleGenerate() {
    setGenerating(true);
    setGenMsg(null);
    try {
      const created = await apiFetch<unknown[]>(`/finance/generate-monthly-charges?period=${period}`, { method: "POST" });
      setGenMsg(
        created.length === 0
          ? "No hay cargos nuevos que generar (ya existen o no hay acuerdos mensuales activos)."
          : `${created.length} cargo${created.length !== 1 ? "s" : ""} generado${created.length !== 1 ? "s" : ""} para ${periodLabel(period)}.`
      );
      await load(period);
    } catch (e) {
      setGenMsg(e instanceof ApiError ? e.message : "Error al generar");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6 space-y-6">
      <PageBreadcrumb pageTitle="Control financiero" />

      {/* Period selector + generate button */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-600 dark:text-gray-400">Periodo:</label>
          <input
            type="month"
            value={period}
            onChange={(e) => { setPeriod(e.target.value); setGenMsg(null); }}
            className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
        </div>
        <Button onClick={handleGenerate} disabled={generating} size="sm">
          {generating ? "Generando..." : "Generar cargos del mes"}
        </Button>
        {genMsg && (
          <span className="text-sm text-gray-600 dark:text-gray-400">{genMsg}</span>
        )}
      </div>

      {error && <p className="text-sm text-error-500">{error}</p>}

      {loading ? (
        <p className="text-sm text-gray-400">Cargando...</p>
      ) : overview && (
        <>
          {/* Stats */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <StatCard
              label={`Total recibido — ${periodLabel(period)}`}
              value={fmtCRC(overview.total_received)}
              color="text-success-700 dark:text-success-400"
            />
            <StatCard
              label="Residentes con mora"
              value={String(overview.overdue_count)}
              color={overview.overdue_count > 0 ? "text-error-700 dark:text-error-400" : "text-gray-700 dark:text-white"}
            />
            <StatCard
              label="Total mora acumulada"
              value={fmtCRC(overview.overdue_total)}
              color={overview.overdue_total > 0 ? "text-error-700 dark:text-error-400" : "text-gray-700 dark:text-white"}
            />
          </div>

          {/* Desglose por pagador */}
          {Object.keys(overview.by_payer_type).length > 0 && (
            <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
              <h3 className="mb-4 text-base font-semibold text-gray-800 dark:text-white">
                Desglose por tipo de pagador — {periodLabel(period)}
              </h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-800 text-sm">
                  <thead>
                    <tr className="text-left text-xs uppercase text-gray-400">
                      <th className="py-2 pr-6">Pagador</th>
                      <th className="py-2 text-right">Total recibido</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                    {Object.entries(overview.by_payer_type)
                      .sort(([, a], [, b]) => b - a)
                      .map(([type, amount]) => (
                        <tr key={type}>
                          <td className="py-2 pr-6 text-gray-700 dark:text-white">
                            {PAYER_LABELS[type] ?? type}
                          </td>
                          <td className="py-2 text-right font-mono text-gray-700 dark:text-white">
                            {fmtCRC(amount)}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Morosidad */}
          <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
            <h3 className="mb-4 text-base font-semibold text-gray-800 dark:text-white">
              Cuentas con mora
              {overdue.length > 0 && (
                <span className="ml-2 inline-flex items-center rounded-full bg-error-50 px-2 py-0.5 text-xs font-medium text-error-700 dark:bg-error-500/10 dark:text-error-400">
                  {overdue.length}
                </span>
              )}
            </h3>

            {overdue.length === 0 ? (
              <p className="text-sm text-gray-400">Sin cuentas morosas. ✓</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-800 text-sm">
                  <thead>
                    <tr className="text-left text-xs uppercase text-gray-400">
                      <th className="py-2 pr-6">Residente</th>
                      <th className="py-2 pr-6">Cargo más antiguo</th>
                      <th className="py-2 pr-6">Días de mora</th>
                      <th className="py-2 text-right pr-6">Saldo pendiente</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                    {overdue.map((entry) => (
                      <tr key={entry.admission_id}>
                        <td className="py-2 pr-6 font-medium text-gray-800 dark:text-white">
                          {entry.resident_name}
                        </td>
                        <td className="py-2 pr-6 text-gray-500">
                          {fmtDate(entry.oldest_charge_date)}
                        </td>
                        <td className="py-2 pr-6">
                          <span className="inline-flex items-center rounded-full bg-error-50 px-2 py-0.5 text-xs font-medium text-error-700 dark:bg-error-500/10 dark:text-error-400">
                            {entry.days_overdue} días
                          </span>
                        </td>
                        <td className="py-2 pr-6 text-right font-mono font-semibold text-error-700 dark:text-error-400">
                          {fmtCRC(entry.balance)}
                        </td>
                        <td className="py-2 text-right">
                          <Link
                            href={`/admissions/${entry.admission_id}/finance`}
                            className="text-brand-500 hover:underline text-xs"
                          >
                            Ver cuenta
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03]">
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
    </div>
  );
}
