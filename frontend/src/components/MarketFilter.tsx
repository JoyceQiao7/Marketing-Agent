import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';
import { Market } from '../lib/types';

interface MarketFilterProps {
  selectedMarket: string;
  onMarketChange: (market: string) => void;
}

export function MarketFilter({ selectedMarket, onMarketChange }: MarketFilterProps) {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMarkets() {
      try {
        const data = await apiClient.getMarkets();
        setMarkets(data);
      } catch (error) {
        console.error('Failed to load markets:', error);
      } finally {
        setLoading(false);
      }
    }
    loadMarkets();
  }, []);

  if (loading) {
    return <div className="text-gray-500">Loading markets...</div>;
  }

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-gray-700">Market Segment</label>
      <select
        value={selectedMarket}
        onChange={(e) => onMarketChange(e.target.value)}
        className="px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="">All Markets</option>
        {markets.map((market) => (
          <option key={market.name} value={market.name}>
            {market.description}
          </option>
        ))}
      </select>
    </div>
  );
}

