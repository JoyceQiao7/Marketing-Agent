/**
 * Button component for triggering crawls
 */
import { useState } from 'react';
import { apiClient } from '@/lib/api';

interface CrawlButtonProps {
  platform: 'reddit' | 'quora';
  onSuccess?: () => void;
}

export default function CrawlButton({ platform, onSuccess }: CrawlButtonProps) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleCrawl = async () => {
    try {
      setLoading(true);
      setMessage(null);
      
      const result = platform === 'reddit' 
        ? await apiClient.triggerRedditCrawl()
        : await apiClient.triggerQuoraCrawl();
      
      setMessage(`✓ Found ${result.items_found} questions, stored ${result.items_stored}`);
      if (onSuccess) onSuccess();
      
      setTimeout(() => setMessage(null), 5000);
    } catch (error: any) {
      setMessage(`✗ Error: ${error.message}`);
      setTimeout(() => setMessage(null), 5000);
    } finally {
      setLoading(false);
    }
  };

  const platformColors = {
    reddit: 'bg-orange-500 hover:bg-orange-600',
    quora: 'bg-red-500 hover:bg-red-600',
  };

  return (
    <div>
      <button
        onClick={handleCrawl}
        disabled={loading}
        className={`${platformColors[platform]} text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors`}
      >
        {loading ? 'Crawling...' : `Crawl ${platform.charAt(0).toUpperCase() + platform.slice(1)}`}
      </button>
      {message && (
        <p className={`text-sm mt-2 ${message.startsWith('✓') ? 'text-green-600' : 'text-red-600'}`}>
          {message}
        </p>
      )}
    </div>
  );
}

