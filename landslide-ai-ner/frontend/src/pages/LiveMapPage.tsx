import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Location, Prediction } from '../types';
import { RiskMap } from '../components/map/RiskMap';
import { LocationDetailPanel } from '../components/map/LocationDetailPanel';
import { RiskBadge } from '../components/ui/RiskBadge';
import { MapPin, Search, Filter } from 'lucide-react';

export const LiveMapPage: React.FC = () => {
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [selectedPrediction, setSelectedPrediction] = useState<Prediction | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [stateFilter, setStateFilter] = useState('ALL');

  useEffect(() => {
    api.getLocations().then((res) => {
      setLocations(res);
      if (res.length > 0) setSelectedLocation(res[0]);
    });
  }, []);

  const handleSelect = async (loc: Location) => {
    setSelectedLocation(loc);
    try {
      const pred = await api.runLocationPrediction(loc.id);
      setSelectedPrediction(pred);
    } catch {
      // fallback
    }
  };

  const filtered = locations.filter((loc) => {
    const matchesSearch = loc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      loc.district.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesState = stateFilter === 'ALL' || loc.state.toUpperCase().includes(stateFilter.toUpperCase());
    return matchesSearch && matchesState;
  });

  return (
    <div className="space-y-4">
      {/* Header & Filter Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-xl border border-slate-800 bg-command-card/90">
        <div>
          <h1 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-blue-400" />
            Northeast India Interactive GIS Geohazard Map
          </h1>
          <p className="text-xs text-slate-400">
            Real-time geospatial risk zones, vulnerable road networks, and sensor placements
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search location or district..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* State Filter */}
          <select
            value={stateFilter}
            onChange={(e) => setStateFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="ALL">All NER States</option>
            <option value="MANIPUR">Manipur</option>
            <option value="ASSAM">Assam</option>
            <option value="NAGALAND">Nagaland</option>
            <option value="MEGHALAYA">Meghalaya</option>
            <option value="MIZORAM">Mizoram</option>
            <option value="ARUNACHAL">Arunachal Pradesh</option>
          </select>
        </div>
      </div>

      {/* Main Grid: Location List + Map */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left List of Locations (4 cols) */}
        <div className="lg:col-span-4 rounded-xl border border-slate-800 bg-command-card p-3 space-y-2 max-h-[650px] overflow-y-auto">
          <div className="text-xs font-bold text-slate-400 px-1 py-1 uppercase tracking-wider">
            Monitored Geozones ({filtered.length})
          </div>
          {filtered.map((loc) => {
            const isSelected = selectedLocation?.id === loc.id;
            return (
              <div
                key={loc.id}
                onClick={() => handleSelect(loc)}
                className={`p-3 rounded-lg border transition cursor-pointer flex items-center justify-between ${
                  isSelected
                    ? 'border-blue-500 bg-blue-950/20'
                    : 'border-slate-800/80 bg-slate-900/50 hover:border-slate-700'
                }`}
              >
                <div>
                  <div className="font-bold text-xs text-slate-200">{loc.name}</div>
                  <div className="text-[11px] text-slate-400">
                    {loc.district}, {loc.state} · {loc.elevation}m
                  </div>
                </div>
                <RiskBadge level={loc.latest_risk_level || 'LOW'} size="sm" />
              </div>
            );
          })}
        </div>

        {/* Right Full-size Map (8 cols) */}
        <div className="lg:col-span-8">
          <RiskMap
            locations={filtered}
            selectedLocation={selectedLocation}
            onSelectLocation={handleSelect}
            className="h-[650px]"
          />
        </div>
      </div>

      {/* Slide-in Detail Panel */}
      {selectedLocation && (
        <LocationDetailPanel
          location={selectedLocation}
          prediction={selectedPrediction}
          onClose={() => setSelectedLocation(null)}
          onReportIncident={() => alert(`Report submission open for ${selectedLocation.name}`)}
          onCreateAlert={() => alert(`Alert broadcast dialog open for ${selectedLocation.name}`)}
        />
      )}
    </div>
  );
};
