import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface RiskTrendChartProps {
  data?: Array<{ timestamp: string; average_risk: number; max_risk: number }>;
}

export const RiskTrendChart: React.FC<RiskTrendChartProps> = ({ data }) => {
  const chartData = data && data.length > 0
    ? data
    : Array.from({ length: 12 }).map((_, i) => {
        const h = (12 - i) * 2;
        const avg = Math.round(25 + i * 3.5 + Math.random() * 4);
        return {
          timestamp: `${h}h ago`,
          average_risk: avg,
          max_risk: Math.min(100, avg + 28),
        };
      });

  return (
    <div className="p-5 rounded-2xl border border-slate-800 bg-command-card/90 flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-bold text-sm text-slate-100">Regional Risk Index Trajectory</h3>
          <p className="text-xs text-slate-400">Mean vs Peak Geotechnical Vulnerability Trend</p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-purple-400 inline-block" />
            <span className="text-slate-400">Peak Risk</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-blue-400 inline-block" />
            <span className="text-slate-400">Average</span>
          </div>
        </div>
      </div>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="timestamp" stroke="#64748b" fontSize={10} tickLine={false} />
            <YAxis domain={[0, 100]} stroke="#64748b" fontSize={10} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#1e293b',
                borderRadius: '8px',
                fontSize: '11px',
                color: '#f8fafc',
              }}
            />
            <ReferenceLine y={80} stroke="#a855f7" strokeDasharray="3 3" label={{ value: 'Critical', fill: '#a855f7', fontSize: 10, position: 'right' }} />
            <ReferenceLine y={60} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'Very High', fill: '#ef4444', fontSize: 10, position: 'right' }} />
            <Line
              type="monotone"
              dataKey="max_risk"
              stroke="#a855f7"
              strokeWidth={2}
              dot={{ r: 3, fill: '#a855f7' }}
              name="Peak Zone Risk"
            />
            <Line
              type="monotone"
              dataKey="average_risk"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 3, fill: '#3b82f6' }}
              name="Mean NER Risk"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
