import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // No bloquear el build de producción por errores de ESLint (variables sin
  // usar, etc.). Son avisos de calidad, no fallos funcionales. El lint se
  // sigue corriendo aparte con `npm run lint` para limpiarlos gradualmente.
  eslint: {
    ignoreDuringBuilds: true,
  },
  async rewrites() {
    // El rewrite a localhost solo aplica en desarrollo, donde el backend
    // corre en el puerto 8005 y el frontend usa rutas relativas (/api/v1).
    // En producción (Vercel) NO se usa: el frontend llama directo a la API
    // de Render vía NEXT_PUBLIC_API_URL, y el proxy a localhost no existiría.
    if (process.env.NODE_ENV !== "development") {
      return [];
    }
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8005/api/:path*",
      },
    ];
  },
  webpack(config) {
    config.module.rules.push({
      test: /\.svg$/,
      use: ["@svgr/webpack"],
    });
    return config;
  },
};

export default nextConfig;
