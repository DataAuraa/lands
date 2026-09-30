import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  color?: 'blue' | 'red' | 'yellow' | 'green' | 'purple';
  trend?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  color = 'blue',
  trend,
}) => {
  const colorMap = {
    blue: {
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/20',
      text: 'text-blue-400',
      iconBg: 'bg-blue-500/20',
    },
    red: {
      bg: 'bg-red-500/10',
      border: 'border-red-500/20',
      text: 'text-red-400',
      iconBg: 'bg-red-500/20',
    },
    yellow: {
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/20',
      text: 'text-amber-400',
      iconBg: 'bg-amber-500/20',
    },
    green: {
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20',
      text: 'text-emerald-400',
      iconBg: 'bg-emerald-500/20',
    },
    purple: {
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/20',
      text: 'text-purple-400',
      iconBg: 'bg-purple-500/20',
    },
  };

  const scheme = colorMap[color];

  return (
    <div className={`p-4 rounded-xl border ${scheme.border} bg-command-card/80 backdrop-blur-md hover:border-slate-600 transition-all duration-200 flex flex-col justify-between`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-slate-400 tracking-wider uppercase">{title}</span>
        <div className={`p-2 rounded-lg ${scheme.iconBg}`}>
          <Icon className={`w-4 h-4 ${scheme.text}`} />
        </div>
      </div>
      <div>
        <div className="text-2xl font-black text-slate-100 font-mono tracking-tight">{value}</div>
        <div className="flex items-center justify-between mt-1">
          {subtitle && <span className="text-xs text-slate-400">{subtitle}</span>}
          {trend && <span className={`text-xs font-semibold ${scheme.text}`}>{trend}</span>}
        </div>
      </div>
    </div>
  );
};
