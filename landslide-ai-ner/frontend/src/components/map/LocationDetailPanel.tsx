import React from 'react';
import { Location, Prediction } from '../../types';
import { RiskBadge } from '../ui/RiskBadge';
import { DataSourceBadge } from '../ui/DataSourceBadge';
import {
  X,
  Mountain,
  Droplets,
  CloudRain,
  Compass,
  AlertTriangle,
  Brain,
  ShieldCheck,
  Send,
  BellPlus
} from 'lucide-react';

interface LocationDetailPanelProps {
  location: Location | null;
  prediction: Prediction | null;
  onClose: () => void;
  onReportIncident?: () => void;
  onCreateAlert?: () => void;
}

export const LocationDetailPanel: React.FC<LocationDetailPanelProps> = ({
  location,
  prediction,
  onClose,
  onReportIncident,
  onCreateAlert,
}) => {
  if (!location) return null;

  const riskScore = prediction?.risk_score ?? location.latest_risk_score ?? 25;
  const riskLevel = prediction?.risk_level ?? location.latest_risk_level ?? 'LOW';
  const topFactors = prediction?.top_factors || [
    'Steep slope gradient (>35°)',
    'High soil pore water pressure',
    'Heavy antecedent 24h precipitation'
  ];

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[420px] bg-slate-900/95 backdrop-blur-xl border-l border-slate-800 p-5 shadow-2xl z-[1000] overflow-y-auto flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <RiskBadge level={riskLevel} size="md" />
              <DataSourceBadge source="DEMO" isSimulation={true} />
            </div>
            <h2 className="text-xl font-bold text-slate-100">{location.name}</h2>
            <p className="text-xs text-slate-400">
              {location.village ? `${location.village}, ` : ''}{location.district}, {location.state}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* AI Prediction Score Banner */}
        <div className="my-4 p-4 rounded-xl bg-command-card border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
              <Brain className="w-4 h-4 text-blue-400" />
              AI Risk Composite Assessment
            </span>
            <span className="text-[11px] font-mono text-slate-500">v1.0-RF-XGB</span>
          </div>
          <div className="flex items-baseline gap-3">
            <span className="text-4xl font-black font-mono text-slate-100">{riskScore}</span>
            <span className="text-xs text-slate-400">/ 100 Early Warning Index</span>
          </div>

          <div className="w-full bg-slate-800 rounded-full h-2 mt-2 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                riskScore > 80 ? 'bg-purple-500' : riskScore > 60 ? 'bg-red-500' : riskScore > 40 ? 'bg-orange-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${riskScore}%` }}
            />
          </div>
        </div>

        {/* Explainability - Top Contributing Factors */}
        <div className="mb-4 p-4 rounded-xl bg-command-card border border-slate-800">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            Why is this location at risk? (XAI)
          </h3>
          <ul className="space-y-2 text-xs text-slate-300">
            {topFactors.map((factor, i) => (
              <li key={i} className="flex items-start gap-2 bg-slate-800/40 p-2 rounded-lg border border-slate-800">
                <span className="text-blue-400 font-mono font-bold">{i + 1}.</span>
                <span>{factor}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Geotechnical & Topographic Specs */}
        <div className="grid grid-cols-2 gap-2 mb-4 text-xs">
          <div className="p-3 rounded-xl bg-command-card border border-slate-800">
            <div className="text-slate-400 flex items-center gap-1 mb-1">
              <Mountain className="w-3.5 h-3.5 text-emerald-400" />
              Slope Angle
            </div>
            <div className="text-base font-bold font-mono text-slate-200">{location.slope}°</div>
          </div>
          <div className="p-3 rounded-xl bg-command-card border border-slate-800">
            <div className="text-slate-400 flex items-center gap-1 mb-1">
              <Compass className="w-3.5 h-3.5 text-cyan-400" />
              Elevation
            </div>
            <div className="text-base font-bold font-mono text-slate-200">{location.elevation} m</div>
          </div>
          <div className="p-3 rounded-xl bg-command-card border border-slate-800">
            <div className="text-slate-400 flex items-center gap-1 mb-1">
              <CloudRain className="w-3.5 h-3.5 text-blue-400" />
              24h Rainfall
            </div>
            <div className="text-base font-bold font-mono text-slate-200">145.2 mm</div>
          </div>
          <div className="p-3 rounded-xl bg-command-card border border-slate-800">
            <div className="text-slate-400 flex items-center gap-1 mb-1">
              <Droplets className="w-3.5 h-3.5 text-purple-400" />
              Soil Saturation
            </div>
            <div className="text-base font-bold font-mono text-slate-200">82.4%</div>
          </div>
        </div>

        {/* Official Guidance Disclaimer */}
        <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-[11px] text-blue-300 flex items-start gap-2 mb-4">
          <ShieldCheck className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
          <p>
            Prototype Decision Support indication. Official instructions from District Disaster Management Authority (DDMA) and State DMA take precedence.
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="pt-3 border-t border-slate-800 flex gap-2">
        <button
          onClick={onReportIncident}
          className="flex-1 py-2.5 px-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition flex items-center justify-center gap-1.5 shadow-lg shadow-blue-600/30"
        >
          <Send className="w-3.5 h-3.5" />
          Report Incident
        </button>
        <button
          onClick={onCreateAlert}
          className="py-2.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-xs transition flex items-center justify-center gap-1.5"
        >
          <BellPlus className="w-3.5 h-3.5" />
          Alert
        </button>
      </div>
    </div>
  );
};
