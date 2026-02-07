/**
 * Library header component with context-aware back button and theme toggle.
 *
 * Shared header for all library pages.
 *
 * @see openspec/changes/physics-based-cell-division-voice/specs/library-header
 */

'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

/**
 * Theme type.
 */
type Theme = 'light' | 'dark';

/**
 * Library header component.
 */
export function LibraryHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const [theme, setTheme] = useState<Theme>('dark');

  // Load theme from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('theme') as Theme | null;
    if (saved) {
      setTheme(saved);
    } else {
      // Detect system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setTheme(prefersDark ? 'dark' : 'light');
    }
  }, []);

  // Toggle theme
  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  // Determine back button text and destination
  let backText = '← Back to AGENTX';
  let backDestination = '/';

  if (pathname === '/library') {
    backText = '← Back to AGENTX';
    backDestination = '/';
  } else if (pathname?.startsWith('/library/')) {
    backText = '← Back to Library';
    backDestination = '/library';
  }

  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-membrane/50 bg-void/80 backdrop-blur-sm">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        {/* Back button */}
        <button
          onClick={() => router.push(backDestination)}
          className="btn btn-ghost"
        >
          {backText}
        </button>

        {/* Title */}
        <h1 className="text-lg font-bold text-nucleus">
          {pathname === '/library' ? 'Design Library' : 'Component Demo'}
        </h1>

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="w-10 h-10 rounded-full flex items-center justify-center bg-membrane hover:bg-cell transition-all hover:scale-105"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
      </div>
    </header>
  );
}
