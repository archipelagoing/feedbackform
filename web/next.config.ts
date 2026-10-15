import type { NextConfig } from "next";

const origin = process.env.FEEDBACKFORM_API_ORIGIN ?? "http://127.0.0.1:8000";
const config: NextConfig = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${origin}/api/:path*` }];
  },
};
export default config;
