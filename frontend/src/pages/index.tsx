/**
 * Dashboard page - main overview
 */
import { useEffect, useState } from 'react';
import StatCard from '@/components/StatCard';
import CrawlButton from '@/components/CrawlButton';
import { useAnalytics } from '@/hooks/useAnalytics';
import { apiClient } from '@/lib/api';

export default function Dashboard() {
  const { analytics, loading, error, refetch } = useAnalytics(true);
  const [apiHealth, setApiHealth] = useState<boolean | null>(null);

  useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      await apiClient.healthCheck();
      setApiHealth(true);
    } catch {
      setApiHealth(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600">Error loading analytics: {error}</p>
        <p className="text-sm text-red-500 mt-2">
          Make sure the backend API is running at {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Monitor your automated marketing agent performance
          </p>
        </div>
        <div className={`px-4 py-2 rounded-lg ${apiHealth ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {apiHealth ? '● API Online' : '● API Offline'}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Questions"
          value={analytics?.total_questions || 0}
          icon="❓"
          color="blue"
        />
        <StatCard
          title="Total Responses"
          value={analytics?.total_responses || 0}
          icon="💬"
          color="green"
        />
        <StatCard
          title="Success Rate"
          value={`${((analytics?.response_success_rate || 0) * 100).toFixed(1)}%`}
          icon="✓"
          color="purple"
        />
        <StatCard
          title="Avg Confidence"
          value={`${((analytics?.avg_confidence_score || 0) * 100).toFixed(1)}%`}
          icon="⭐"
          color="orange"
        />
      </div>

      {/* Crawl Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Manual Crawl</h2>
        <p className="text-gray-600 mb-6">
          Trigger a manual crawl to fetch new questions from platforms
        </p>
        <div className="flex space-x-4">
          <CrawlButton platform="reddit" onSuccess={refetch} />
          <CrawlButton platform="quora" onSuccess={refetch} />
        </div>
      </div>

      {/* Questions by Status */}
      {analytics?.questions_by_status && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Questions by Status</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(analytics.questions_by_status).map(([status, count]) => (
              <div key={status} className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-gray-900">{count}</p>
                <p className="text-sm text-gray-600 capitalize mt-1">{status}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Questions by Platform */}
      {analytics?.questions_by_platform && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Questions by Platform</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(analytics.questions_by_platform).map(([platform, count]) => (
              <div key={platform} className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-gray-900">{count}</p>
                <p className="text-sm text-gray-600 capitalize mt-1">{platform}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
        <h2 className="text-xl font-bold mb-2">Need Help?</h2>
        <p className="mb-4 opacity-90">
          View the API documentation or check the README for customization instructions
        </p>
        <div className="flex space-x-4">
          <a
            href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/docs`}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-white text-blue-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
          >
            API Docs
          </a>
          <a
            href="/questions"
            className="bg-white/20 backdrop-blur-sm text-white px-4 py-2 rounded-lg font-medium hover:bg-white/30 transition-colors"
          >
            View All Questions
          </a>
        </div>
      </div>
    </div>
  );
}

