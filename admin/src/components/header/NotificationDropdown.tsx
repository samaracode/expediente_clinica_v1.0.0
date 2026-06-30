"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { NotificationItem } from "@/types";
import { Dropdown } from "../ui/dropdown/Dropdown";

const TYPE_CONFIG: Record<
  NotificationItem["type"],
  { icon: string; color: string; linkPath: (id: number) => string }
> = {
  upcoming_appointment: {
    icon: "📅",
    color: "text-blue-600 bg-blue-50 dark:bg-blue-900/20",
    linkPath: (id) => `/admissions/${id}/consultations`,
  },
  overdue_exit_pass: {
    icon: "⚠️",
    color: "text-error-600 bg-error-50 dark:bg-error-900/20",
    linkPath: (id) => `/admissions/${id}/exit-passes`,
  },
  upcoming_stage_end: {
    icon: "🕐",
    color: "text-warning-600 bg-warning-50 dark:bg-warning-900/20",
    linkPath: (id) => `/admissions/${id}/treatment-plan`,
  },
  overdue_medication: {
    icon: "💊",
    color: "text-error-600 bg-error-50 dark:bg-error-900/20",
    linkPath: (id) => `/admissions/${id}/medications`,
  },
  absent_without_leave: {
    icon: "🚨",
    color: "text-error-600 bg-error-50 dark:bg-error-900/20",
    linkPath: (id) => `/admissions/${id}`,
  },
  overdue_balance: {
    icon: "₡",
    color: "text-orange-600 bg-orange-50 dark:bg-orange-900/20",
    linkPath: (id) => `/admissions/${id}/finance`,
  },
};

export default function NotificationDropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    apiFetch<NotificationItem[]>("/notifications")
      .then(setNotifications)
      .catch(() => setNotifications([]))
      .finally(() => setLoaded(true));
  }, []);

  const count = notifications.length;

  return (
    <div className="relative">
      <button
        className="relative dropdown-toggle flex items-center justify-center text-gray-500 transition-colors bg-white border border-gray-200 rounded-full hover:text-gray-700 h-11 w-11 hover:bg-gray-100 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-white"
        onClick={() => setIsOpen((v) => !v)}
      >
        {loaded && count > 0 && (
          <span className="absolute -top-0.5 -right-0.5 z-10 flex h-4 w-4 items-center justify-center rounded-full bg-error-500 text-white text-[9px] font-bold leading-none">
            {count > 9 ? "9+" : count}
          </span>
        )}
        <svg
          className="fill-current"
          width="20"
          height="20"
          viewBox="0 0 20 20"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M10.75 2.29248C10.75 1.87827 10.4143 1.54248 10 1.54248C9.58583 1.54248 9.25004 1.87827 9.25004 2.29248V2.83613C6.08266 3.20733 3.62504 5.9004 3.62504 9.16748V14.4591H3.33337C2.91916 14.4591 2.58337 14.7949 2.58337 15.2091C2.58337 15.6234 2.91916 15.9591 3.33337 15.9591H4.37504H15.625H16.6667C17.0809 15.9591 17.4167 15.6234 17.4167 15.2091C17.4167 14.7949 17.0809 14.4591 16.6667 14.4591H16.375V9.16748C16.375 5.9004 13.9174 3.20733 10.75 2.83613V2.29248ZM14.875 14.4591V9.16748C14.875 6.47509 12.6924 4.29248 10 4.29248C7.30765 4.29248 5.12504 6.47509 5.12504 9.16748V14.4591H14.875ZM8.00004 17.7085C8.00004 18.1228 8.33583 18.4585 8.75004 18.4585H11.25C11.6643 18.4585 12 18.1228 12 17.7085C12 17.2943 11.6643 16.9585 11.25 16.9585H8.75004C8.33583 16.9585 8.00004 17.2943 8.00004 17.7085Z"
            fill="currentColor"
          />
        </svg>
      </button>

      <Dropdown
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        className="absolute -right-[160px] mt-[17px] flex w-[340px] flex-col rounded-2xl border border-gray-200 bg-white p-3 shadow-theme-lg dark:border-gray-800 dark:bg-gray-dark sm:w-[360px] lg:right-0"
      >
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-gray-100 dark:border-gray-700">
          <h5 className="text-base font-semibold text-gray-800 dark:text-gray-200">
            Alertas
            {count > 0 && (
              <span className="ml-2 rounded-full bg-error-100 px-2 py-0.5 text-xs font-bold text-error-700 dark:bg-error-900/30 dark:text-error-400">
                {count}
              </span>
            )}
          </h5>
          <button
            onClick={() => setIsOpen(false)}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            <svg className="fill-current" width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path fillRule="evenodd" clipRule="evenodd" d="M6.21967 7.28131C5.92678 6.98841 5.92678 6.51354 6.21967 6.22065C6.51256 5.92775 6.98744 5.92775 7.28033 6.22065L11.999 10.9393L16.7176 6.22078C17.0105 5.92789 17.4854 5.92788 17.7782 6.22078C18.0711 6.51367 18.0711 6.98855 17.7782 7.28144L13.0597 12L17.7782 16.7186C18.0711 17.0115 18.0711 17.4863 17.7782 17.7792C17.4854 18.0721 17.0105 18.0721 16.7176 17.7792L11.999 13.0607L7.28033 17.7794C6.98744 18.0722 6.51256 18.0722 6.21967 17.7794C5.92678 17.4865 5.92678 17.0116 6.21967 16.7187L10.9384 12L6.21967 7.28131Z" fill="currentColor" />
            </svg>
          </button>
        </div>

        <ul className="flex flex-col max-h-[380px] overflow-y-auto custom-scrollbar gap-1">
          {!loaded && (
            <li className="px-3 py-4 text-center text-sm text-gray-400">Cargando...</li>
          )}
          {loaded && count === 0 && (
            <li className="px-3 py-8 text-center">
              <p className="text-sm text-gray-400">Sin alertas pendientes.</p>
              <p className="text-xs text-gray-300 mt-1 dark:text-gray-600">Todo en orden</p>
            </li>
          )}
          {notifications.map((n, i) => {
            const cfg = TYPE_CONFIG[n.type];
            return (
              <li key={i}>
                <Link
                  href={cfg.linkPath(n.entity_id)}
                  onClick={() => setIsOpen(false)}
                  className="flex items-start gap-3 rounded-lg px-3 py-2.5 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
                >
                  <span className={`mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-base ${cfg.color}`}>
                    {cfg.icon}
                  </span>
                  <span className="min-w-0">
                    <span className="block text-sm text-gray-800 dark:text-white/90 leading-snug">
                      {n.message}
                    </span>
                    {n.due_date && (
                      <span className="block text-xs text-gray-400 mt-0.5">
                        {new Date(n.due_date + "T12:00:00").toLocaleDateString("es-CR", {
                          weekday: "short",
                          day: "numeric",
                          month: "short",
                        })}
                      </span>
                    )}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      </Dropdown>
    </div>
  );
}
