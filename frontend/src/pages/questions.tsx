/**
 * Questions page - view and filter all questions
 */
import { useState } from 'react';
import QuestionCard from '@/components/QuestionCard';
import { useQuestions } from '@/hooks/useQuestions';
import { Question } from '@/lib/types';

export default function QuestionsPage() {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const { questions, loading, error, refetch } = useQuestions(statusFilter, true);

  const statuses = ['all', 'pending', 'processing', 'answered', 'ignored', 'error'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading questions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600">Error loading questions: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Questions</h1>
          <p className="text-gray-600 mt-2">
            Browse and manage crawled questions from social media platforms
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
        >
          ↻ Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700">Filter by status:</span>
          {statuses.map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status === 'all' ? '' : status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                (status === 'all' && !statusFilter) || statusFilter === status
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status === 'all' ? 'All' : status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <p className="text-gray-600">
          Showing <span className="font-bold text-gray-900">{questions.length}</span> questions
          {statusFilter && (
            <span>
              {' '}with status: <span className="font-bold text-blue-600">{statusFilter}</span>
            </span>
          )}
        </p>
      </div>

      {/* Questions Grid */}
      {questions.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <p className="text-gray-500 text-lg">No questions found</p>
          <p className="text-gray-400 text-sm mt-2">
            Try triggering a manual crawl from the dashboard
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {questions.map((question: Question) => (
            <QuestionCard
              key={question.id}
              question={question}
              onViewDetails={(q) => {
                console.log('View details:', q);
                // You can implement a modal or detail page here
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

