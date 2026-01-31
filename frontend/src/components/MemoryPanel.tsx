/**
 * Memory Panel component for visualizing memories.
 *
 * Future component for memory visualization (C005 placeholder).
 */

'use client';

import { useState, useEffect } from 'react';
import { useSearchMemory, useStoreMemory, useMemoryHealth } from '../hooks/useMemory';
import type { SearchResult, TemporalType } from '../lib/schemas/memory';

interface MemoryPanelProps {
  userId: string;
}

export function MemoryPanel({ userId }: MemoryPanelProps) {
  const [query, setQuery] = useState('');
  const [timeFilter, setTimeFilter] = useState<'recent' | 'historical' | 'all'>('all');
  const [results, setResults] = useState<SearchResult[]>([]);
  const { searchMemory, loading: searching } = useSearchMemory();
  const { storeMemory, loading: storing } = useStoreMemory();
  const { health, loading: healthLoading } = useMemoryHealth();

  useEffect(() => {
    // Check health on mount
    useMemoryHealth().checkHealth();
  }, []);

  const handleSearch = async () => {
    const response = await searchMemory({
      query,
      user_id: userId,
      tier: 3,
      time_filter: timeFilter,
      max_results: 10,
    });

    if (response) {
      setResults(response.results || []);
    }
  };

  const handleStore = async (content: string, temporalType: TemporalType) => {
    const response = await storeMemory({
      content,
      user_id: userId,
      temporal_type: temporalType,
      tier: 3,
    });

    if (response) {
      console.log('Memory stored:', response);
    }
  };

  return (
    <div className="p-4 border rounded-lg bg-white dark:bg-gray-800">
      <h2 className="text-xl font-bold mb-4">Memory Panel</h2>

      {/* Health Status */}
      {health && (
        <div className="mb-4 p-2 bg-green-100 dark:bg-green-900 rounded">
          <p className="text-sm">
            Status: {health.status} | Qdrant: {health.qdrant_connected ? 'Connected' : 'Disconnected'}
          </p>
        </div>
      )}

      {/* Store Memory */}
      <div className="mb-4">
        <h3 className="font-semibold mb-2">Store Memory</h3>
        <textarea
          className="w-full p-2 border rounded"
          placeholder="Enter memory content..."
          rows={3}
        />
        <div className="mt-2">
          <button
            onClick={() => handleStore('Test memory', 'fact')}
            disabled={storing}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {storing ? 'Storing...' : 'Store as Fact'}
          </button>
        </div>
      </div>

      {/* Search Memories */}
      <div>
        <h3 className="font-semibold mb-2">Search Memories</h3>
        <input
          type="text"
          className="w-full p-2 border rounded mb-2"
          placeholder="Search query..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="mb-2">
          <label className="mr-4">
            <input
              type="radio"
              name="timeFilter"
              value="all"
              checked={timeFilter === 'all'}
              onChange={() => setTimeFilter('all')}
            />
            {' '}All
          </label>
          <label className="mr-4">
            <input
              type="radio"
              name="timeFilter"
              value="recent"
              checked={timeFilter === 'recent'}
              onChange={() => setTimeFilter('recent')}
            />
            {' '}Recent
          </label>
          <label>
            <input
              type="radio"
              name="timeFilter"
              value="historical"
              checked={timeFilter === 'historical'}
              onChange={() => setTimeFilter('historical')}
            />
            {' '}Historical
          </label>
        </div>
        <button
          onClick={handleSearch}
          disabled={searching}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
        >
          {searching ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="mt-4">
          <h3 className="font-semibold mb-2">Results ({results.length})</h3>
          <div className="space-y-2">
            {results.map((result) => (
              <div
                key={result.memory_id}
                className="p-3 border rounded bg-gray-50 dark:bg-gray-700"
              >
                <p className="text-sm mb-1">{result.content}</p>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Type: {result.temporal_type}</span>
                  <span>Score: {result.score.toFixed(2)}</span>
                  {result.superseded && <span className="text-red-500">Outdated</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
