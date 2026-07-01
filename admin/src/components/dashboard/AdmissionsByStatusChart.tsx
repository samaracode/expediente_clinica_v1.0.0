"use client";
import dynamic from "next/dynamic";
import { ApexOptions } from "apexcharts";
import type { StatusCountItem } from "@/types";

const ReactApexChart = dynamic(() => import("react-apexcharts"), { ssr: false });

interface Props {
  data: StatusCountItem[];
}

const STATUS_LABELS: Record<string, string> = {
  intake_pending: "Intake pendiente",
  consents_pending: "Consentimientos",
  assessment_in_progress: "Evaluación",
  treatment_active: "Tratamiento activo",
  discharged: "Egresado",
  abandoned: "Abandonó",
};

const STATUS_COLORS = [
  "#94A3B8",
  "#FBBF24",
  "#60A5FA",
  "#34D399",
  "#A78BFA",
  "#F87171",
];

export default function AdmissionsByStatusChart({ data }: Props) {
  const labels = data.map((d) => STATUS_LABELS[d.status] ?? d.status);
  const series = data.map((d) => d.count);

  const options: ApexOptions = {
    chart: {
      fontFamily: "Outfit, sans-serif",
      type: "donut",
      height: 300,
    },
    colors: STATUS_COLORS.slice(0, data.length),
    labels,
    legend: {
      position: "bottom",
      horizontalAlign: "center",
      fontSize: "13px",
    },
    dataLabels: { enabled: false },
    plotOptions: {
      pie: {
        donut: {
          size: "65%",
          labels: {
            show: true,
            total: {
              show: true,
              label: "Total",
              fontSize: "14px",
              fontWeight: "600",
              color: "#6B7280",
              formatter: (w) =>
                String(w.globals.seriesTotals.reduce((a: number, b: number) => a + b, 0)),
            },
          },
        },
      },
    },
    tooltip: {
      y: { formatter: (v) => `${v} admisiones` },
    },
  };

  if (data.length === 0) {
    return (
      <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white/90">
          Admisiones por estado
        </h3>
        <p className="mt-4 text-sm text-gray-400">Sin datos disponibles</p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white/90">
        Admisiones por estado
      </h3>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Distribución del embudo clínico
      </p>
      <div className="mt-4">
        <ReactApexChart options={options} series={series} type="donut" height={300} />
      </div>
    </div>
  );
}
