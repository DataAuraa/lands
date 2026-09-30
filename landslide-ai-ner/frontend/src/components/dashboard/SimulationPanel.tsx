import React, { useState } from 'react';
import { Play, Pause, RotateCcw, ChevronRight, CheckCircle2, AlertOctagon } from 'lucide-react';
import { RiskBadge } from '../ui/RiskBadge';

const SCENARIO_STEPS = [
  { step: 1, title: 'Normal Baseline Weather', desc: 'Seasonal conditions in Noney Valley. Low precipitation and stable geotechnical readings.', risk: 'LOW', score: 14.5, rf: '2 mm/h', sm: '38%' },
  { step: 2, title: 'Heavy Rainfall Begins', desc: 'Monsoon cloudburst front enters hill range. Precipitation starts accumulating on slopes.', risk: 'MODERATE', score: 28.0, rf: '18 mm/h', sm: '48%' },
  { step: 3, title: 'Continuous Downpour', desc: 'Continuous torrential rain. Runoff coefficient increases as topsoil reaches initial saturation.', risk: 'MODERATE', score: 38.5, rf: '32 mm/h', sm: '62%' },
  { step: 4, title: 'Soil Moisture Surges', desc: 'IoT piezometers register rapid rise in pore-water pressure along steep road cuts.', risk: 'HIGH', score: 48.0, rf: '42 mm/h', sm: '76%' },
  { step: 5, title: 'AI Risk Reaches HIGH', desc: 'Multi-factor trigger crosses 50. Slope factor of safety deteriorates.', risk: 'HIGH', score: 58.0, rf: '48 mm/h', sm: '84%' },
  { step: 6, title: 'Severe Saturation (VERY HIGH)', desc: 'Antecedent moisture reaches critical threshold. Soil cohesion drops significantly.', risk: 'VERY_HIGH', score: 74.0, rf: '55 mm/h', sm: '91%' },
  { step: 7, title: 'Emergency Alert Generated', desc: 'Early Warning Engine broadcasts automated warning bulletin to State DMA and DEOC.', risk: 'CRITICAL', score: 82.0, rf: '60 mm/h', sm: '94%' },
  { step: 8, title: 'Live GIS Heatmap Updates', desc: 'MapLibre GL layer transitions risk buffer zone to Critical purple contour.', risk: 'CRITICAL', score: 88.5, rf: '62 mm/h', sm: '95%' },
  { step: 9, title: 'Multilingual Warning Dispatched', desc: 'Villagers receive emergency notifications in English, Hindi, and Assamese/Manipuri.', risk: 'CRITICAL', score: 91.0, rf: '58 mm/h', sm: '96%' },
  { step: 10, title: 'Field Officer Submits Crack Report', desc: 'On-ground patrol discovers 15cm tension cracks along crown and submits photo via mobile web.', risk: 'CRITICAL', score: 93.0, rf: '52 mm/h', sm: '96%' },
  { step: 11, title: 'District Authority Verifies Report', desc: 'Disaster authority reviews field report, marks VERIFIED, and mobilizes SDRF rescue units.', risk: 'CRITICAL', score: 95.0, rf: '40 mm/h', sm: '97%' },
  { step: 12, title: 'Active Incident Displayed on GIS', desc: 'Road closure pin added to command center map. Feedback loop closed.', risk: 'CRITICAL', score: 86.0, rf: '25 mm/h', sm: '94%' },
];

export const SimulationPanel: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);

  const activeStepData = SCENARIO_STEPS[currentStep - 1];

  const handleNext = () => {
    setCurrentStep((prev) => (prev < 12 ? prev + 1 : 1));
  };

  const handleReset = () => {
    setCurrentStep(1);
    setIsPlaying(false);
  };

  return (
    <div className="p-5 rounded-2xl border border-slate-800 bg-command-card/90 backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-purple-500/20 text-purple-400">
            <AlertOctagon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-100">Live Disaster Event Simulation</h3>
            <p className="text-xs text-slate-400">12-Step Noney Railway Yard Geo-Hazard Scenario</p>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition ${
              isPlaying
                ? 'bg-amber-600 text-white hover:bg-amber-500'
                : 'bg-blue-600 text-white hover:bg-blue-500'
            }`}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span>{isPlaying ? 'Pause' : 'Auto Play'}</span>
          </button>
          <button
            onClick={handleNext}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1 transition"
          >
            <span>Next</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleReset}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 transition"
            title="Reset to Step 1"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Progress Stepper Bar */}
      <div className="grid grid-cols-12 gap-1 my-4">
        {SCENARIO_STEPS.map((s) => (
          <button
            key={s.step}
            onClick={() => setCurrentStep(s.step)}
            className={`h-2 rounded-full transition-all duration-300 ${
              s.step === currentStep
                ? 'bg-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.8)] scale-y-125'
                : s.step < currentStep
                ? 'bg-blue-500/60'
                : 'bg-slate-800'
            }`}
            title={`Step ${s.step}: ${s.title}`}
          />
        ))}
      </div>

      {/* Active Step Details */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold text-blue-400">PHASE {activeStepData.step}/12:</span>
            <h4 className="font-bold text-sm text-slate-200">{activeStepData.title}</h4>
          </div>
          <RiskBadge level={activeStepData.risk} size="sm" />
        </div>

        <p className="text-xs text-slate-300 mb-3">{activeStepData.desc}</p>

        {/* Telemetry at this step */}
        <div className="grid grid-cols-4 gap-2 text-center text-xs">
          <div className="p-2 rounded-lg bg-command-card border border-slate-800">
            <div className="text-[10px] text-slate-400">Risk Score</div>
            <div className="font-mono font-bold text-sm text-purple-400">{activeStepData.score}</div>
          </div>
          <div className="p-2 rounded-lg bg-command-card border border-slate-800">
            <div className="text-[10px] text-slate-400">Intensity</div>
            <div className="font-mono font-bold text-sm text-blue-400">{activeStepData.rf}</div>
          </div>
          <div className="p-2 rounded-lg bg-command-card border border-slate-800">
            <div className="text-[10px] text-slate-400">Soil Saturation</div>
            <div className="font-mono font-bold text-sm text-cyan-400">{activeStepData.sm}</div>
          </div>
          <div className="p-2 rounded-lg bg-command-card border border-slate-800">
            <div className="text-[10px] text-slate-400">Early Warning</div>
            <div className="font-mono font-bold text-sm text-slate-200">{activeStepData.risk}</div>
          </div>
        </div>
      </div>
    </div>
  );
};
