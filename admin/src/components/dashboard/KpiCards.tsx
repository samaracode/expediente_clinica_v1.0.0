"use client";
import { GroupIcon, ArrowUpIcon, ArrowDownIcon } from "@/icons";

interface Props {
  activeResidents: number;
  admissionsThisMonth: number;
  dischargesThisMonth: number;
  outstandingBalance?: number | null;
}

function KpiCard({
  label,
  value,
  icon,
  colorClass,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
  colorClass: string;
}) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-white/[0.03] md:p-6">
      <div
        className={`flex items-center justify-center w-12 h-12 rounded-xl ${colorClass}`}
      >
        {icon}
      </div>
      <div className="mt-5">
        <span className="text-sm text-gray-500 dark:text-gray-400">{label}</span>
        <h4 className="mt-2 text-2xl font-bold text-gray-800 dark:text-white/90">
          {value}
        </h4>
      </div>
    </div>
  );
}

function formatCRC(amount: number): string {
  return new Intl.NumberFormat("es-CR", {
    style: "currency",
    currency: "CRC",
    maximumFractionDigits: 0,
  }).format(amount);
}

export default function KpiCards({
  activeResidents,
  admissionsThisMonth,
  dischargesThisMonth,
  outstandingBalance,
}: Props) {
  const cards = [
    {
      label: "Residentes activos",
      value: String(activeResidents),
      icon: <GroupIcon className="text-brand-600 size-6" />,
      colorClass: "bg-brand-50 dark:bg-brand-500/10",
    },
    {
      label: "Ingresos del mes",
      value: String(admissionsThisMonth),
      icon: <ArrowUpIcon className="text-success-600 size-6" />,
      colorClass: "bg-success-50 dark:bg-success-500/10",
    },
    {
      label: "Egresos del mes",
      value: String(dischargesThisMonth),
      icon: <ArrowDownIcon className="text-error-500 size-6" />,
      colorClass: "bg-error-50 dark:bg-error-500/10",
    },
  ];

  if (outstandingBalance != null) {
    cards.push({
      label: "Saldo por cobrar",
      value: formatCRC(outstandingBalance),
      icon: (
        <svg
          className="text-warning-600 size-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 8c-2.21 0-4 1.34-4 3s1.79 3 4 3 4 1.34 4 3-1.79 3-4 3m0-18v2m0 16v2"
          />
        </svg>
      ),
      colorClass: "bg-warning-50 dark:bg-warning-500/10",
    });
  }

  return (
    <div
      className={`grid grid-cols-1 gap-4 sm:grid-cols-2 ${
        cards.length === 4 ? "xl:grid-cols-4" : "xl:grid-cols-3"
      } md:gap-6`}
    >
      {cards.map((c) => (
        <KpiCard key={c.label} {...c} />
      ))}
    </div>
  );
}
