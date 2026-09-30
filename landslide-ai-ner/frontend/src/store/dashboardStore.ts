import { create } from 'zustand';
import { DashboardSummary, Location, Alert } from '../types';

interface DashboardState {
  summary: DashboardSummary | null;
  selectedLocation: Location | null;
  activeLanguage: string;
  simulationStep: number;
  isSimulating: boolean;
  setSummary: (s: DashboardSummary) => void;
  setSelectedLocation: (l: Location | null) => void;
  setLanguage: (lang: string) => void;
  setSimulationStep: (step: number) => void;
  setIsSimulating: (sim: boolean) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  summary: null,
  selectedLocation: null,
  activeLanguage: 'en',
  simulationStep: 1,
  isSimulating: false,
  setSummary: (summary) => set({ summary }),
  setSelectedLocation: (selectedLocation) => set({ selectedLocation }),
  setLanguage: (activeLanguage) => set({ activeLanguage }),
  setSimulationStep: (simulationStep) => set({ simulationStep }),
  setIsSimulating: (isSimulating) => set({ isSimulating }),
}));
