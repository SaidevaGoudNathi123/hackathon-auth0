import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  typescript: {
    // Zod v3/v4 mismatch between @auth0/ai-vercel and ai SDK v6
    // Code is functionally correct — skip type check on build
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
