/**
 * Custom hook for fetching analytics data
 */
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { Analytics } from '@/lib/types';

export function useAnalytics(autoRefresh: boolean = false) {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getAnalytics();
      setAnalytics(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();

    if (autoRefresh) {
      const interval = setInterval(fetchAnalytics, 60000); // Refresh every 60 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  return { analytics, loading, error, refetch: fetchAnalytics };
}

