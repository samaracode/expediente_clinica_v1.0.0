"use client";
import dynamic from "next/dynamic";
import { ApexOptions } from "apexcharts";
import type { MonthlyFlowItem } from "@/types";

const ReactApexChart = dynamic(() => import("react-apexcharts"), { ssr: false });

interface Props {
  data: MonthlyFlowItem[];
}

function shortMonth(yyyymm: string): string {
  const [year, month] = yyyymm.split("-");
  const date = new Date(Number(year), Number(month) - 1, 1);
  return date.toLocaleString("es-CR", { month: "short" });
}

export default function MonthlyFlowChart({ data }: Props) {
  const categories = data.map((d) => shortMonth(d.month));
  const admissions = data.map((d) => d.admissions);
  const discharges = data.map((d) => d.discharges);

  const options: ApexOptions = {
    chart: {
      fontFamily: "Outfit, sans-serif",
      type: "bar",
      height: 280,
      toolbar: { show: false },
    },
    colors: ["#465FFF", "#F04438"],
    plotOptions: {
      bar: {
        columnWidth: "55%",
        borderRadius: 4,
      },
    },
    dataLabels: { enabled: false },
    xaxis: {
      categories,
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: {
      tickAmount: 4,
      labels: { formatter: (v) => String(Math.round(v)) },
    },
    legend: {
      position: "top",
      horizontalAlign: "right",
      markers: { size: 8 },
    },
    grid: {
      borderColor: "#E4E7EC",
      strokeDashArray: 4,
      yaxis: { lines: { show: true } },
    },
    tooltip: {
      y: { formatter: (v) => `${v} residentes` },
    },
  };

  const series = [
    { name: "Ingresos", data: admissions },
    { name: "Egresos", data: discharges },
  ];

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white/90">
        Ingresos vs egresos
      </h3>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Últimos 6 meses
      </p>
      <div className="mt-4">
        <ReactApexChart options={options} series={series} type="bar" height={280} />
      </div>
    </div>
  );
}
