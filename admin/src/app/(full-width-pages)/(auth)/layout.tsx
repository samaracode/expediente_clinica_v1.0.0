import ThemeTogglerTwo from "@/components/common/ThemeTogglerTwo";
import { ThemeProvider } from "@/context/ThemeContext";
import Image from "next/image";
import React from "react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative bg-white z-1 dark:bg-gray-900">
      <ThemeProvider>
        <div className="flex flex-col items-center justify-center min-h-screen w-full dark:bg-gray-900 px-4">
          <div className="mb-6">
            <Image
              width={240}
              height={135}
              src="/images/logo/zoe_logo.png"
              alt="Logo ZOE"
              unoptimized
            />
          </div>
          {children}
          <div className="fixed bottom-6 right-6 z-50 hidden sm:block">
            <ThemeTogglerTwo />
          </div>
        </div>
      </ThemeProvider>
    </div>
  );
}
