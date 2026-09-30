import React from 'react';
import { Radio, AlertTriangle, CheckCircle, WifiOff } from 'lucide-react';

interface DataSourceBadgeProps {
  source?: string;
  isSimulation?: boolean;
  timestamp?: string;
}

export const DataSourceBadge: React.FC<DataSourceBadgeProps> = ({
  source = 'DEMO',
  isSimulation = true,
  timestamp,
}) => {
  const isSim = isSimulation || source.toUpperCase().includes('DEMO') || source.toUpperCase().includes('SIM');

  if (isSim) {
    return (
      <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
        <AlertTriangle className="w-3 h-3 text-amber-400" />
        <span>SIMULATION MODE (DEMO)</span>
        {timestamp && <span className="opacity-60 text-[10px]">· {timestamp}</span>}
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
      <CheckCircle className="w-3 h-3 text-emerald-400" />
      <span>LIVE: {source}</span>
      {timestamp && <span className="opacity-60 text-[10px]">· {timestamp}</span>}
    </div>
  );
};
