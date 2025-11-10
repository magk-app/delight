/** @type {import('next').NextConfig} */
const path = require("path");

const nextConfig = {
  reactStrictMode: true,
  // Fix for multiple lockfile warning - set workspace root explicitly
  outputFileTracingRoot: path.join(__dirname, "../../"),
  experimental: {
    serverActions: {
      allowedOrigins: ["localhost:3000"],
    },
  },
};

module.exports = nextConfig;
