/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Allow requests from mobile devices on same WiFi network
  allowedDevOrigins: [
    'http://192.168.1.4:3014',  // Mobile access via local network
    'http://localhost:3014',
  ],
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8014',
    NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'Prototype 14',
  },
};

module.exports = nextConfig;
