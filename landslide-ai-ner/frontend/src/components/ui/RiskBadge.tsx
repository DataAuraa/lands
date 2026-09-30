import React from 'react';
import { RiskLevel } from '../../types';

interface RiskBadgeProps {
  level: RiskLevel | string;
  size?: 'sm' | 'md' | 'lg';
  showPulse?: boolean;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  size = 'md',
  showPulse = true,
}) => {
  const normLevel = (level || 'LOW').toUpperCase();

  const colorStyles: Record<string, string> = {
    LOW: 'bg-green-500/15 text-green-400 border-green-500/30',
    MODERATE: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
    HIGH: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
    VERY_HIGH: 'bg-red-500/20 text-red-400 border-red-500/40',
    CRITICAL: 'bg-purple-500/25 text-purple-300 border-purple-500/50 shadow-[0_0_12px_rgba(168,85,247,0.4)]',
  };

  const dotColors: Record<string, string> = {
    LOW: 'bg-green-400',
    MODERATE: 'bg-yellow-400',
    HIGH: 'bg-orange-400',
    VERY_HIGH: 'bg-red-400',
    CRITICAL: 'bg-purple-400',
  };

  const sizeStyles = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs font-semibold px-2.5 py-1 gap-1.5',
    lg: 'text-sm font-bold px-3.5 py-1.5 gap-2',
  };

  const style = colorStyles[normLevel] || colorStyles.LOW;
  const dotColor = dotColors[normLevel] || dotColors.LOW;
  const isCritical = normLevel === 'CRITICAL';

  return (
    <span
      className={`inline-flex items-center rounded-full border ${style} ${sizeStyles[size]} transition-all duration-300`}
    >
      <span className="relative flex h-2 w-2">
        {(showPulse || isCritical) && (
          <span
            className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${dotColor}`}
          />
        )}
        <span className={`relative inline-flex rounded-full h-2 w-2 ${dotColor}`} />
      </span>
      <span>{normLevel.replace('_', ' ')}</span>
    </span>
  );
};
