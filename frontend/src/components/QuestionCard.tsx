/**
 * Question card component for displaying question details
 */
import { Question } from '@/lib/types';

interface QuestionCardProps {
  question: Question;
  onViewDetails?: (question: Question) => void;
}

export default function QuestionCard({ question, onViewDetails }: QuestionCardProps) {
  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    processing: 'bg-blue-100 text-blue-800',
    answered: 'bg-green-100 text-green-800',
    ignored: 'bg-gray-100 text-gray-800',
    error: 'bg-red-100 text-red-800',
  };

  const platformColors = {
    reddit: 'bg-orange-500',
    quora: 'bg-red-500',
    twitter: 'bg-blue-400',
    other: 'bg-gray-500',
  };

  const formatMarket = (market: string) => {
    return market.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-2 flex-wrap gap-2">
          <span className={`${platformColors[question.platform]} text-white px-3 py-1 rounded-full text-xs font-medium uppercase`}>
            {question.platform}
          </span>
          <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-xs font-medium">
            📊 {formatMarket(question.market)}
          </span>
          <span className={`${statusColors[question.status]} px-3 py-1 rounded-full text-xs font-medium capitalize`}>
            {question.status}
          </span>
        </div>
        <div className="flex items-center text-sm text-gray-500">
          <span>↑ {question.upvotes}</span>
        </div>
      </div>

      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {question.title}
      </h3>

      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
        {question.content}
      </p>

      <div className="flex items-center justify-between text-sm">
        <div className="text-gray-500">
          <span className="font-medium">by {question.author}</span>
          {' • '}
          <span>{new Date(question.created_at).toLocaleDateString()}</span>
        </div>
        
        <div className="flex space-x-2">
          <a
            href={question.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            View Post →
          </a>
          {onViewDetails && (
            <button
              onClick={() => onViewDetails(question)}
              className="text-purple-600 hover:text-purple-800 font-medium ml-4"
            >
              Details
            </button>
          )}
        </div>
      </div>

      {question.tags.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {question.tags.map((tag, index) => (
            <span
              key={index}
              className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

