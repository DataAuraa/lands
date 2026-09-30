import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { SensorReading } from '../types';
import { SensorStatusCard } from '../components/ui/SensorStatusCard';
import { Cpu, Wifi, BatteryLow, AlertCircle, Filter } from 'lucide-react';

export const SensorsPage: React.FC = () => {
  const [sensors, setSensors] = useState<SensorReading[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  useEffect(() => {
    api.getSensors().then((res) => setSensors(res));
  }, []);

  const onlineCount = sensors.filter((s) => s.latest_status !== 'OFFLINE').length;
  const lowBatCount = sensors.filter((s) => s.latest_status === 'LOW_BATTERY').length;
  const offlineCount = sensors.filter((s) => s.latest_status === 'OFFLINE').length;

  const filtered = sensors.filter((s) => {
    if (filterStatus === 'ALL') return true;
    return s.latest_status === filterStatus;
  });

  return (
    <div className="space-y-6">
      {/* Title & Filters */}
      <div className="p-4 rounded-xl border border-slate-800 bg-command-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-blue-400" />
            Geotechnical IoT Sensor Network
          </h1>
          <p className="text-xs text-slate-400">
            Real-time piezometers and soil moisture nodes monitoring vulnerable slope corridors
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <button
            onClick={() => setFilterStatus('ALL')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
              filterStatus === 'ALL' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            All ({sensors.length})
          </button>
          <button
            onClick={() => setFilterStatus('ONLINE')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
              filterStatus === 'ONLINE' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Online ({onlineCount})
          </button>
          <button
            onClick={() => setFilterStatus('LOW_BATTERY')}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
              filterStatus === 'LOW_BATTERY' ? 'bg-amber-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            Low Battery ({lowBatCount})
          </button>
        </div>
      </div>

      {/* Sensor KPI Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/10 flex items-center gap-3">
          <Wifi className="w-5 h-5 text-emerald-400" />
          <div>
            <div className="text-xs text-emerald-300">Nodes Operational</div>
            <div className="text-xl font-bold font-mono text-emerald-200">{onlineCount} / {sensors.length}</div>
          </div>
        </div>

        <div className="p-4 rounded-xl border border-amber-500/20 bg-amber-500/10 flex items-center gap-3">
          <BatteryLow className="w-5 h-5 text-amber-400" />
          <div>
            <div className="text-xs text-amber-300">Low Battery Warning</div>
            <div className="text-xl font-bold font-mono text-amber-200">{lowBatCount} Nodes</div>
          </div>
        </div>

        <div className="p-4 rounded-xl border border-red-500/20 bg-red-500/10 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <div>
            <div className="text-xs text-red-300">Offline / No Signal</div>
            <div className="text-xl font-bold font-mono text-red-200">{offlineCount} Nodes</div>
          </div>
        </div>
      </div>

      {/* Sensor Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filtered.map((sensor) => (
          <SensorStatusCard key={sensor.sensor_id} sensor={sensor} />
        ))}
      </div>
    </div>
  );
};
