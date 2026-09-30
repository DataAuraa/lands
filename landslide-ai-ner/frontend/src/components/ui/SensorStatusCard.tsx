import React from 'react';
import { SensorReading } from '../../types';
import { BatteryCharging, BatteryLow, Cpu, Droplets } from 'lucide-react';

interface SensorStatusCardProps {
  sensor: SensorReading;
  onClick?: () => void;
}

export const SensorStatusCard: React.FC<SensorStatusCardProps> = ({ sensor, onClick }) => {
  const moisture = sensor.latest_soil_moisture ?? 45.0;
  const battery = sensor.latest_battery ?? 95.0;
  const status = sensor.latest_status || 'ONLINE';

  const statusColors = {
    ONLINE: 'bg-emerald-400',
    OFFLINE: 'bg-red-400',
    LOW_BATTERY: 'bg-amber-400',
    ERROR: 'bg-rose-500',
  };

  const statusBg = {
    ONLINE: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
    OFFLINE: 'text-red-400 border-red-500/30 bg-red-500/10',
    LOW_BATTERY: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
    ERROR: 'text-rose-400 border-rose-500/30 bg-rose-500/10',
  };

  return (
    <div
      onClick={onClick}
      className="p-3.5 rounded-xl border border-slate-800 bg-command-card/80 hover:border-slate-700 transition cursor-pointer flex flex-col justify-between"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-blue-500/15 text-blue-400">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-slate-200 font-mono">{sensor.sensor_id}</div>
            <div className="text-[11px] text-slate-400 truncate max-w-[120px]">{sensor.name}</div>
          </div>
        </div>
        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${statusBg[status] || statusBg.ONLINE}`}>
          {status}
        </span>
      </div>

      <div className="space-y-2 mt-2">
        <div>
          <div className="flex justify-between text-[11px] text-slate-400 mb-1">
            <span className="flex items-center gap-1">
              <Droplets className="w-3 h-3 text-cyan-400" />
              Soil Saturation
            </span>
            <span className="font-mono font-bold text-cyan-300">{moisture}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                moisture > 80 ? 'bg-purple-500' : moisture > 60 ? 'bg-cyan-400' : 'bg-blue-500'
              }`}
              style={{ width: `${Math.min(100, moisture)}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-[11px] text-slate-400 mb-1">
            <span className="flex items-center gap-1">
              {battery < 20 ? (
                <BatteryLow className="w-3 h-3 text-amber-400" />
              ) : (
                <BatteryCharging className="w-3 h-3 text-emerald-400" />
              )}
              Battery
            </span>
            <span className="font-mono text-slate-300">{battery}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className={`h-full rounded-full ${battery < 20 ? 'bg-amber-400' : 'bg-emerald-400'}`}
              style={{ width: `${Math.min(100, battery)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
