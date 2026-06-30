"use client";

import Link from "next/link";
import Button from "@/components/ui/button/Button";

export default function UnauthorizedPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center p-8 text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-error-50 dark:bg-error-900/20">
        <svg className="h-8 w-8 text-error-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
        </svg>
      </div>
      <h1 className="mb-2 text-2xl font-semibold text-gray-800 dark:text-white">Sin acceso</h1>
      <p className="mb-6 text-sm text-gray-500">
        Tu rol no tiene permiso para acceder a esta sección. Contacta al administrador si crees que esto es un error.
      </p>
      <Link href="/">
        <Button variant="outline">Volver al inicio</Button>
      </Link>
    </div>
  );
}
