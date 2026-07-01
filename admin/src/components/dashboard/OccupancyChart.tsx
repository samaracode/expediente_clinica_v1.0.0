"use client";
import dynamic from "next/dynamic";
import { ApexOptions } from "apexcharts";

const ReactApexChart = dynamic(() => import("react-apexcharts"), { ssr: false });

interface Props {
  active: number;
  capacity: number;
  occupancyPct: number;
  waitlistCount: number;
}

export default function OccupancyChart({ active, capacity, occupancyPct, waitlistCount }: Props) {
  const options: ApexOptions = {
    colors: ["#465FFF"],
    chart: {
      fontFamily: "Outfit, sans-serif",
      type: "radialBar",
      height: 280,
      sparkline: { enabled: true },
    },
    plotOptions: {
      radialBar: {
        startAngle: -90,
        endAngle: 90,
        hollow: { size: "70%" },
        track: {
          background: "#E4E7EC",
          strokeWidth: "100%",
          margin: 5,
        },
        dataLabels: {
          name: { show: false },
          value: {
            fontSize: "32px",
            fontWeight: "700",
            offsetY: -30,
            color: "#1D2939",
            formatter: (val) => `${val}%`,
          },
        },
      },
    },
    fill: { type: "solid", colors: ["#465FFF"] },
    stroke: { lineCap: "round" },
  };

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white/90">
        Ocupación
      </h3>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Camas ocupadas vs capacidad total
      </p>

      <div className="mt-4 max-h-[280px]">
        <ReactApexChart
          options={options}
          series={[occupancyPct]}
          type="radialBar"
          height={280}
        />
      </div>

      <div className="mt-2 flex items-center justify-center gap-8 border-t border-gray-100 pt-4 dark:border-gray-800">
        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">Activos</p>
          <p className="mt-1 text-xl font-bold text-gray-800 dark:text-white/90">
            {active}
          </p>
        </div>
        <div className="h-8 w-px bg-gray-200 dark:bg-gray-700" />
        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">Capacidad</p>
          <p className="mt-1 text-xl font-bold text-gray-800 dark:text-white/90">
            {capacity}
          </p>
        </div>
        <div className="h-8 w-px bg-gray-200 dark:bg-gray-700" />
        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">En espera</p>
          <p className="mt-1 text-xl font-bold text-gray-800 dark:text-white/90">
            {waitlistCount}
          </p>
        </div>
      </div>
    </div>
  );
}
