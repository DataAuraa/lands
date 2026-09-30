import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { WeatherData, Location } from '../types';
import { DataSourceBadge } from '../components/ui/DataSourceBadge';
import { RainfallChart } from '../components/dashboard/RainfallChart';
import {
  CloudRain,
  Thermometer,
  Droplets,
  Wind,
  Gauge,
  Calendar,
  CloudLightning
} from 'lucide-react';

export const WeatherPage: React.FC = () => {
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocId, setSelectedLocId] = useState<number>(2); // Default Noney
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [forecast, setForecast] = useState<any[]>([]);

  useEffect(() => {
    api.getLocations().then((res) => {
      setLocations(res);
      if (res.length > 0 && !selectedLocId) setSelectedLocId(res[0].id);
    });
  }, []);

  useEffect(() => {
    if (!selectedLocId) return;
    api.getCurrentWeather(selectedLocId).then((w) => setWeather(w));
    api.getWeatherForecast(selectedLocId).then((fc) => setForecast(fc.forecast || []));
  }, [selectedLocId]);

  const selectedLoc = locations.find((l) => l.id === selectedLocId);

  return (
    <div className="space-y-6">
      {/* Header & Location Selector */}
      <div className="p-4 rounded-xl border border-slate-800 bg-command-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <DataSourceBadge source={weather?.source || 'DEMO (SIMULATED)'} isSimulation={true} />
          </div>
          <h1 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <CloudRain className="w-5 h-5 text-blue-400" />
            Northeast India Hydrometeorological Telemetry
          </h1>
          <p className="text-xs text-slate-400">
            High-frequency rainfall accumulation windows and early warning thresholds
          </p>
        </div>

        {/* Location Dropdown */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-medium">Select Station:</span>
          <select
            value={selectedLocId}
            onChange={(e) => setSelectedLocId(Number(e.target.value))}
            className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-medium"
          >
            {locations.map((loc) => (
              <option key={loc.id} value={loc.id}>
                {loc.name} ({loc.district}, {loc.state})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Atmospheric Metric Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl border border-slate-800 bg-command-card flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-blue-500/20 text-blue-400">
            <CloudRain className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">24h Rainfall</div>
            <div className="text-xl font-bold font-mono text-slate-100">{weather?.rainfall_24h ?? 185} mm</div>
          </div>
        </div>

        <div className="p-4 rounded-xl border border-slate-800 bg-command-card flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/20 text-cyan-400">
            <Droplets className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Relative Humidity</div>
            <div className="text-xl font-bold font-mono text-slate-100">{weather?.humidity ?? 88}%</div>
          </div>
        </div>

        <div className="p-4 rounded-xl border border-slate-800 bg-command-card flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400">
            <Thermometer className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Ambient Temp</div>
            <div className="text-xl font-bold font-mono text-slate-100">{weather?.temperature ?? 22.4}°C</div>
          </div>
        </div>

        <div className="p-4 rounded-xl border border-slate-800 bg-command-card flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-purple-500/20 text-purple-400">
            <Gauge className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Barometer</div>
            <div className="text-xl font-bold font-mono text-slate-100">{weather?.pressure ?? 1004} hPa</div>
          </div>
        </div>
      </div>

      {/* Multi-Window Cumulative Rainfall vs Landslide Triggers */}
      <div className="p-5 rounded-2xl border border-slate-800 bg-command-card">
        <h3 className="font-bold text-sm text-slate-200 mb-3 flex items-center gap-2">
          <CloudLightning className="w-4 h-4 text-amber-400" />
          Disaster Warning Multi-Window Rainfall Accumulation
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-6 gap-3 text-center text-xs">
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div className="text-slate-400 text-[11px] mb-1">1-Hour Burst</div>
            <div className="font-mono font-bold text-base text-blue-400">{weather?.rainfall_1h ?? 18} mm</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div className="text-slate-400 text-[11px] mb-1">3-Hour Window</div>
            <div className="font-mono font-bold text-base text-blue-400">{weather?.rainfall_3h ?? 45} mm</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div className="text-slate-400 text-[11px] mb-1">6-Hour Window</div>
            <div className="font-mono font-bold text-base text-blue-400">{weather?.rainfall_6h ?? 82} mm</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div className="text-slate-400 text-[11px] mb-1">12-Hour Window</div>
            <div className="font-mono font-bold text-base text-blue-400">{weather?.rainfall_12h ?? 125} mm</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div className="text-slate-400 text-[11px] mb-1">24-Hour Critical</div>
            <div className="font-mono font-bold text-base text-purple-400">{weather?.rainfall_24h ?? 185} mm</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div className="text-slate-400 text-[11px] mb-1">72-Hour Antecedent</div>
            <div className="font-mono font-bold text-base text-purple-400">{weather?.rainfall_72h ?? 310} mm</div>
          </div>
        </div>
      </div>

      {/* Hourly Rainfall Chart */}
      <RainfallChart />

      {/* 3-Day Forecast Table */}
      <div className="p-5 rounded-2xl border border-slate-800 bg-command-card">
        <h3 className="font-bold text-sm text-slate-200 mb-3 flex items-center gap-2">
          <Calendar className="w-4 h-4 text-blue-400" />
          72-Hour Quantitative Precipitation Forecast (QPF)
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-2 text-xs">
          {forecast.slice(0, 6).map((item, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center">
              <div className="text-slate-500 text-[10px] mb-1">+{idx * 6 + 6}h</div>
              <div className="font-mono font-bold text-blue-300 text-sm">{item.expected_rainfall} mm</div>
              <div className="text-slate-400 text-[11px] mt-1">{item.temperature}°C · {item.humidity}%</div>
              <span className={`inline-block mt-2 px-2 py-0.5 rounded text-[10px] font-bold ${
                item.risk_indicator === 'HIGH' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
              }`}>
                {item.risk_indicator}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
