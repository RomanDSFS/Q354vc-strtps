import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,

  async rewrites() {
    return [
      {
        source: "/api/startups/:path*",
        destination: "http://localhost:8000/startups/:path*",
      },
      {
        source: "/api/auth/:path*", // ✅ добавляем
        destination: "http://localhost:8000/auth/:path*",
      },
      {
        source: "/api/investors/:path*",
        destination: "http://localhost:8000/investors/:path*",
      },      
    ];
  },
};

export default nextConfig;
