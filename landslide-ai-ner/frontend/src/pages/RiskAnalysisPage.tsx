import React, { useState } from 'react';
import { api } from '../services/api';
import { Prediction } from '../types';
import { RiskBadge } from '../components/ui/RiskBadge';
import {
  Brain,
  Play,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Sparkles,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';

export const RiskAnalysisPage: React.FC = () => {
  const [formData, setFormData] = useState({
    rainfall_24h: 120,
    soil_moisture: 78,
    slope: 38,
    elevation: 850,
    historical_susceptibility: 0.76,
    rainfall_72h: 210,
    rainfall_1h: 25,
    change_score: 0.15,
  });

  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [isPredicting, setIsPredicting] = useState(false);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsPredicting(true);
    try {
      const res = await api.predictDirect(formData);
      setPrediction(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsPredicting(false);
    }
  };

  // Preset scenarios
  const applyPreset = (preset: string) => {
    if (preset === 'CRITICAL') {
      setFormData({
        rainfall_24h: 240,
        soil_moisture: 94,
        slope: 42,
        elevation: 820,
        historical_susceptibility: 0.88,
        rainfall_72h: 320,
        rainfall_1h: 45,
        change_score: 0.45,
      });
    } else if (preset === 'MODERATE') {
      setFormData({
        rainfall_24h: 45,
        soil_moisture: 52,
        slope: 24,
        elevation: 600,
        historical_susceptibility: 0.45,
        rainfall_72h: 70,
        rainfall_1h: 6,
        change_score: 0.05,
      });
    } else {
      setFormData({
        rainfall_24h: 10,
        soil_moisture: 32,
        slope: 16,
        elevation: 350,
        historical_susceptibility: 0.25,
        rainfall_72h: 18,
        rainfall_1h: 1,
        change_score: 0.0,
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="p-4 rounded-xl border border-slate-800 bg-command-card flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-400" />
            AI Landslide Risk Prediction & Explainability Engine
          </h1>
          <p className="text-xs text-slate-400">
            Multi-factor geotechnical inference pipeline calibrated for Northeast India mountain terrain
          </p>
        </div>

        {/* Presets */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-medium">Load Preset:</span>
          <button
            onClick={() => applyPreset('LOW')}
            className="px-2.5 py-1 rounded bg-green-500/10 text-green-400 border border-green-500/30 text-xs font-semibold hover:bg-green-500/20 transition"
          >
            Safe Baseline
          </button>
          <button
            onClick={() => applyPreset('MODERATE')}
            className="px-2.5 py-1 rounded bg-yellow-500/10 text-yellow-400 border border-yellow-500/30 text-xs font-semibold hover:bg-yellow-500/20 transition"
          >
            Monsoon Shower
          </button>
          <button
            onClick={() => applyPreset('CRITICAL')}
            className="px-2.5 py-1 rounded bg-purple-500/20 text-purple-300 border border-purple-500/40 text-xs font-bold hover:bg-purple-500/30 transition animate-pulse"
          >
            Extreme Cloudburst
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Input Form (7 cols) */}
        <form onSubmit={handlePredict} className="lg:col-span-7 p-5 rounded-2xl border border-slate-800 bg-command-card/90 space-y-4">
          <h3 className="font-bold text-sm text-slate-200 flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-400" />
            Input Geotechnical & Hydrometeorological Parameters
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                24-Hour Accumulated Rainfall (mm)
              </label>
              <input
                type="number"
                value={formData.rainfall_24h}
                onChange={(e) => setFormData({ ...formData, rainfall_24h: Number(e.target.value) })}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono text-slate-100 focus:outline-none focus:border-blue-500"
              />
              <span className="text-[10px] text-slate-500">Critical threshold: &gt;150mm</span>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Soil Moisture Saturation (%)
              </label>
              <input
                type="number"
                value={formData.soil_moisture}
                onChange={(e) => setFormData({ ...formData, soil_moisture: Number(e.target.value) })}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono text-slate-100 focus:outline-none focus:border-blue-500"
              />
              <span className="text-[10px] text-slate-500">Volumetric water content</span>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Slope Angle (Degrees °)
              </label>
              <input
                type="number"
                value={formData.slope}
                onChange={(e) => setFormData({ ...formData, slope: Number(e.target.value) })}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono text-slate-100 focus:outline-none focus:border-blue-500"
              />
              <span className="text-[10px] text-slate-500">Angle of hill slope cut</span>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Elevation (Meters MSL)
              </label>
              <input
                type="number"
                value={formData.elevation}
                onChange={(e) => setFormData({ ...formData, elevation: Number(e.target.value) })}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono text-slate-100 focus:outline-none focus:border-blue-500"
              />
              <span className="text-[10px] text-slate-500">Topographic height</span>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                Historical Susceptibility (0.0 to 1.0)
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.historical_susceptibility}
                onChange={(e) => setFormData({ ...formData, historical_susceptibility: Number(e.target.value) })}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono text-slate-100 focus:outline-none focus:border-blue-500"
              />
              <span className="text-[10px] text-slate-500">Geological formation susceptibility</span>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">
                72h Antecedent Rainfall (mm)
              </label>
              <input
                type="number"
                value={formData.rainfall_72h}
                onChange={(e) => setFormData({ ...formData, rainfall_72h: Number(e.target.value) })}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono text-slate-100 focus:outline-none focus:border-blue-500"
              />
              <span className="text-[10px] text-slate-500">Multi-day antecedent moisture index</span>
            </div>
          </div>

          <button
            type="submit"
            disabled={isPredicting}
            className="w-full py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition shadow-lg shadow-purple-600/30"
          >
            {isPredicting ? (
              <span>Running Model Inference...</span>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Run AI Risk Assessment (POST /api/ml/predict)</span>
              </>
            )}
          </button>
        </form>

        {/* Right Output Panel (5 cols) */}
        <div className="lg:col-span-5 p-5 rounded-2xl border border-slate-800 bg-command-card/90 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <span className="font-bold text-xs text-slate-300 uppercase tracking-wider">
                Prediction Inference Output
              </span>
              <span className="text-[10px] font-mono text-blue-400 px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20">
                PROTOTYPE HEURISTIC
              </span>
            </div>

            {prediction ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-3xl font-black font-mono text-slate-100">
                      {prediction.risk_score}
                      <span className="text-sm font-normal text-slate-400"> / 100</span>
                    </div>
                    <div className="text-xs text-slate-400">Calculated Risk Index</div>
                  </div>
                  <RiskBadge level={prediction.risk_level} size="lg" />
                </div>

                <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 grid grid-cols-2 gap-2 text-center text-xs">
                  <div>
                    <div className="text-slate-500 text-[10px]">Probability</div>
                    <div className="font-mono font-bold text-slate-200">{prediction.probability}</div>
                  </div>
                  <div>
                    <div className="text-slate-500 text-[10px]">Confidence</div>
                    <div className="font-mono font-bold text-slate-200">{prediction.confidence}</div>
                  </div>
                </div>

                {/* Explainability factors */}
                <div>
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                    Top Contributing Geohazard Drivers (XAI)
                  </h4>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {prediction.top_factors.map((factor, idx) => (
                      <li key={idx} className="p-2 rounded-lg bg-slate-800/40 border border-slate-800 flex items-start gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
                        <span>{factor}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="py-16 text-center text-xs text-slate-500 space-y-2">
                <Brain className="w-8 h-8 text-slate-600 mx-auto" />
                <p>Click "Run AI Risk Assessment" to evaluate geotechnical factors.</p>
              </div>
            )}
          </div>

          <div className="mt-4 p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-[10px] text-blue-300">
            {prediction?.disclaimer ||
              'This is an AI-generated risk indication and should be interpreted with official disaster-management guidance.'}
          </div>
        </div>
      </div>
    </div>
  );
};
