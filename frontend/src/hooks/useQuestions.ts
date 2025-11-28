/**
 * Custom hook for fetching and managing questions with multi-market support
 */
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { Question } from '@/lib/types';

interface UseQuestionsParams {
  status?: string;
  market?: string;
  platform?: string;
  min_score?: number;
  limit?: number;
  autoRefresh?: boolean;
}

export function useQuestions(params?: UseQuestionsParams) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getQuestions({
        status: params?.status,
        market: params?.market,
        platform: params?.platform,
        min_score: params?.min_score,
        limit: params?.limit || 100,
      });
      setQuestions(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch questions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();

    if (params?.autoRefresh) {
      const interval = setInterval(fetchQuestions, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [params?.status, params?.market, params?.platform, params?.min_score, params?.autoRefresh]);

  return { questions, loading, error, refetch: fetchQuestions };
}
