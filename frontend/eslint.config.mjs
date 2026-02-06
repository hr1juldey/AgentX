/**
 * ESLint Flat Config (ESLint 9+)
 * Using Next.js recommended config.
 */

import { FlatCompat } from '@eslint/eslintrc';
import { dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const nextConfig = compat.config({
  extends: ['next/core-web-vitals', 'next/typescript'],
});

/** @type {import("eslint").Linter.Config[]} */
export default [
  {
    ignores: [
      '.next/',
      'node_modules/',
      'out/',
      'build/',
      'dist/',
    ],
  },
  ...nextConfig.map(config => ({
    ...config,
    rules: {
      ...config.rules,
      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
        },
      ],
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  })),
];
