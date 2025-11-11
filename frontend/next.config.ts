import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  output: 'standalone',

  trailingSlash: true,
  poweredByHeader: false,
  compress: true,
  experimental: {
    optimizeCss: true,
  },
};

export default nextConfig;
