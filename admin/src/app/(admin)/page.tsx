"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { DashboardSummary } from "@/types";
import KpiCards from "@/components/dashboard/KpiCards";
import OccupancyChart from "@/components/dashboard/OccupancyChart";
import MonthlyFlowChart from "@/components/dashboard/MonthlyFlowChart";
import AdmissionsByStatusChart from "@/components/dashboard/AdmissionsByStatusChart";

function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded-2xl bg-gray-100 dark:bg-gray-800 ${className ?? ""}`}
    />
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<DashboardSummary>("/dashboard/summary")
      .then(setData)
      .catch((e) => setError(e.message ?? "Error al cargar el dashboard"));
  }, []);

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[300px]">
        <p className="text-sm text-error-500">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="grid grid-cols-12 gap-4 md:gap-6">
        <div className="col-span-12">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4 md:gap-6">
            {[0, 1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
        </div>
        <div className="col-span-12 xl:col-span-5">
          <Skeleton className="h-80" />
        </div>
        <div className="col-span-12 xl:col-span-7">
          <Skeleton className="h-80" />
        </div>
        <div className="col-span-12">
          <Skeleton className="h-80" />
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-12 gap-4 md:gap-6">
      {/* KPI cards — fila superior */}
      <div className="col-span-12">
        <KpiCards
          activeResidents={data.active_residents}
          admissionsThisMonth={data.admissions_this_month}
          dischargesThisMonth={data.discharges_this_month}
          outstandingBalance={data.outstanding_balance}
        />
      </div>

      {/* Gráfico radial de ocupación */}
      <div className="col-span-12 xl:col-span-5">
        <OccupancyChart
          active={data.active_residents}
          capacity={data.capacity}
          occupancyPct={data.occupancy_pct}
          waitlistCount={data.waitlist_count}
        />
      </div>

      {/* Dona: admisiones por estado */}
      <div className="col-span-12 xl:col-span-7">
        <AdmissionsByStatusChart data={data.admissions_by_status} />
      </div>

      {/* Barras: flujo mensual */}
      <div className="col-span-12">
        <MonthlyFlowChart data={data.monthly_flow} />
      </div>
    </div>
  );
}
