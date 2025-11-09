/**
 * Custom hook for fetching and managing questions
 */
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { Question } from '@/lib/types';

export function useQuestions(status?: string, autoRefresh: boolean = false) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getQuestions(status);
      setQuestions(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch questions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();

    if (autoRefresh) {
      const interval = setInterval(fetchQuestions, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [status, autoRefresh]);

  return { questions, loading, error, refetch: fetchQuestions };
}

