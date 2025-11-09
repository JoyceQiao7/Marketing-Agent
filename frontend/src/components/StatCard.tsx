/**
 * Stat card component for displaying metrics
 */
interface StatCardProps {
  title: string;
  value: string | number;
  icon?: string;
  color?: string;
}

export default function StatCard({ title, value, icon, color = 'blue' }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        {icon && (
          <div className={`${colorClasses[color as keyof typeof colorClasses]} w-12 h-12 rounded-lg flex items-center justify-center text-white text-xl`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}

