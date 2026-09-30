import React from 'react';
import { useDashboardStore } from '../../store/dashboardStore';
import { Radio, AlertTriangle, ShieldAlert } from 'lucide-react';

export const SystemHeader: React.FC = () => {
  const { summary } = useDashboardStore();

  const counts = summary?.risk_distribution || {
    LOW: 5,
    MODERATE: 4,
    HIGH: 2,
    VERY_HIGH: 1,
    CRITICAL: 0,
  };

  return (
    <div className="bg-slate-950/80 border-b border-slate-800/80 text-xs px-4 py-2 flex flex-wrap items-center justify-between gap-3 backdrop-blur-md">
      {/* Left: Simulation Alert Banner */}
      <div className="flex items-center gap-2">
        <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[11px]">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
          SIMULATION / DEMO MODE
        </span>
        <span className="hidden md:inline text-slate-400 text-[11px]">
          Calibrated synthetic models active. Not official government telemetry.
        </span>
      </div>

      {/* Center: Live Hazard Counters */}
      <div className="flex items-center gap-1.5 font-mono text-[11px]">
        <span className="text-slate-400 mr-1 hidden sm:inline">NER STATUS:</span>
        <span className="px-2 py-0.5 rounded bg-green-500/20 text-green-300 border border-green-500/30">
          LOW: {counts.LOW || 0}
        </span>
        <span className="px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-300 border border-yellow-500/30">
          MOD: {counts.MODERATE || 0}
        </span>
        <span className="px-2 py-0.5 rounded bg-orange-500/20 text-orange-300 border border-orange-500/30">
          HIGH: {counts.HIGH || 0}
        </span>
        <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-300 border border-red-500/30">
          VERY HIGH: {counts.VERY_HIGH || 0}
        </span>
        <span className="px-2 py-0.5 rounded bg-purple-500/25 text-purple-300 border border-purple-500/40 font-bold animate-pulse">
          CRITICAL: {counts.CRITICAL || 0}
        </span>
      </div>

      {/* Right: Live Connection Pulse */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-emerald-400 font-mono text-[11px]">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping inline-block" />
          <span>TELEMETRY STREAM: LIVE</span>
        </div>
      </div>
    </div>
  );
};
