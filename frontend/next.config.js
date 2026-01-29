/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  webpack: (config) => {
    config.externals = {
      'pyodide': 'pyodide',
    };
    return config;
  },
};

module.exports = nextConfig;
