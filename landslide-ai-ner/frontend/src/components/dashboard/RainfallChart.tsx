import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface RainfallChartProps {
  data?: Array<{ timestamp: string; rainfall_1h: number; rainfall_24h: number }>;
}

export const RainfallChart: React.FC<RainfallChartProps> = ({ data }) => {
  // Fallback realistic monsoon trend data if not provided
  const chartData = data && data.length > 0
    ? data
    : Array.from({ length: 24 }).map((_, i) => {
        const h = 24 - i;
        const rf = Math.round((Math.sin(i / 3) * 15 + 18 + Math.random() * 8) * 10) / 10;
        return {
          timestamp: `${h}h ago`,
          rainfall_1h: rf,
          rainfall_24h: Math.round(rf * (i + 1) * 0.4),
        };
      });

  return (
    <div className="p-5 rounded-2xl border border-slate-800 bg-command-card/90 flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-bold text-sm text-slate-100">Precipitation Accumulation</h3>
          <p className="text-xs text-slate-400">24-Hour Rainfall Rate (mm/h) vs Thresholds</p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-blue-500 inline-block" />
            <span className="text-slate-400">Rate (mm/h)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-0.5 bg-red-400 inline-block" />
            <span className="text-red-400">Warning (30mm/h)</span>
          </div>
        </div>
      </div>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="rainGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="timestamp" stroke="#64748b" fontSize={10} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#1e293b',
                borderRadius: '8px',
                fontSize: '11px',
                color: '#f8fafc',
              }}
            />
            <ReferenceLine y={30} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'Warning', fill: '#ef4444', fontSize: 10, position: 'right' }} />
            <Area
              type="monotone"
              dataKey="rainfall_1h"
              stroke="#3b82f6"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#rainGradient)"
              name="Rainfall Rate (mm/h)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
