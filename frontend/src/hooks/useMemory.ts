/**
 * Memory API hooks for frontend.
 *
 * React hooks for memory operations.
 * Matches backend REST endpoints from C005 memory-rag.
 */

import { useState, useCallback } from 'react';
import {
  StoreMemoryRequestSchema,
  SearchMemoryRequestSchema,
  ConsolidateMemoryRequestSchema,
  type StoreMemoryRequest,
  type SearchMemoryRequest,
  type ConsolidateMemoryRequest,
  type StoreMemoryResponse,
  type SearchMemoryResponse,
  type ConsolidateMemoryResponse,
  type HealthResponse,
} from '../lib/schemas/memory';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8015';

// Store memory hook
export function useStoreMemory() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const storeMemory = useCallback(async (request: StoreMemoryRequest): Promise<StoreMemoryResponse | null> => {
    setLoading(true);
    setError(null);

    try {
      // Validate request
      const validated = StoreMemoryRequestSchema.parse(request);

      const response = await fetch(`${BACKEND_URL}/api/v1/memory/store`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(validated),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to store memory';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { storeMemory, loading, error };
}

// Search memory hook
export function useSearchMemory() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchMemory = useCallback(async (request: SearchMemoryRequest): Promise<SearchMemoryResponse | null> => {
    setLoading(true);
    setError(null);

    try {
      // Validate request
      const validated = SearchMemoryRequestSchema.parse(request);

      const response = await fetch(`${BACKEND_URL}/api/v1/memory/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(validated),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to search memories';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { searchMemory, loading, error };
}

// Consolidate memory hook
export function useConsolidateMemory() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const consolidateMemory = useCallback(async (request: ConsolidateMemoryRequest): Promise<ConsolidateMemoryResponse | null> => {
    setLoading(true);
    setError(null);

    try {
      // Validate request
      const validated = ConsolidateMemoryRequestSchema.parse(request);

      const response = await fetch(`${BACKEND_URL}/api/v1/memory/consolidate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(validated),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to consolidate memories';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { consolidateMemory, loading, error };
}

// Health check hook
export function useMemoryHealth() {
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<HealthResponse | null>(null);

  const checkHealth = useCallback(async (): Promise<boolean> => {
    setLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/memory/health`);

      if (!response.ok) {
        setHealth(null);
        return false;
      }

      const data = await response.json();
      setHealth(data);
      return data.status === 'healthy';
    } catch {
      setHealth(null);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return { checkHealth, health, loading };
}

// Active states hook
export function useActiveStates(userId: string) {
  const [loading, setLoading] = useState(false);
  const [states, setStates] = useState<any>(null);

  const fetchActiveStates = useCallback(async () => {
    setLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/memory/active-states/${userId}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setStates(data);
    } catch (err) {
      console.error('Failed to fetch active states:', err);
      setStates(null);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  return { fetchActiveStates, states, loading };
}
