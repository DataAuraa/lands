import React, { useEffect, useRef } from 'react';
import { Location } from '../../types';
import { Layers, ShieldAlert, Activity, Navigation } from 'lucide-react';

interface RiskMapProps {
  locations: Location[];
  selectedLocation: Location | null;
  onSelectLocation: (loc: Location) => void;
  className?: string;
}

declare const L: any;

export const RiskMap: React.FC<RiskMapProps> = ({
  locations,
  selectedLocation,
  onSelectLocation,
  className = 'h-[500px]',
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);

  useEffect(() => {
    if (!mapContainerRef.current || typeof L === 'undefined') return;

    if (!mapInstanceRef.current) {
      // Centered on Northeast India (NER: Assam, Manipur, Nagaland, Meghalaya, Mizoram, Arunachal)
      const map = L.map(mapContainerRef.current, {
        center: [25.5, 93.2],
        zoom: 7,
        zoomControl: false,
      });

      L.control.zoom({ position: 'bottomright' }).addTo(map);

      // Dark CartoDB / OpenStreetMap tile layer
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        maxZoom: 18,
      }).addTo(map);

      mapInstanceRef.current = map;
    }

    const map = mapInstanceRef.current;

    // Clear existing markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    const riskColors: Record<string, string> = {
      LOW: '#22c55e',
      MODERATE: '#eab308',
      HIGH: '#f97316',
      VERY_HIGH: '#ef4444',
      CRITICAL: '#a855f7',
    };

    // Render monitored location geozones
    locations.forEach((loc) => {
      const level = (loc.latest_risk_level || 'LOW').toUpperCase();
      const color = riskColors[level] || '#3b82f6';
      const isSelected = selectedLocation?.id === loc.id;
      const isCritical = level === 'CRITICAL';

      const radius = isSelected ? 18 : isCritical ? 14 : 10;

      const marker = L.circleMarker([loc.latitude, loc.longitude], {
        radius: radius,
        fillColor: color,
        color: isSelected ? '#ffffff' : color,
        weight: isSelected ? 3 : 2,
        opacity: 0.9,
        fillOpacity: 0.75,
      }).addTo(map);

      marker.bindTooltip(
        `<div style="font-family: inherit; font-size: 12px; line-height: 1.4;">
          <strong>${loc.name}</strong><br/>
          <span>${loc.district}, ${loc.state}</span><br/>
          <span style="color: ${color}; font-weight: bold;">Risk: ${loc.latest_risk_score ?? 25}/100 (${level.replace('_', ' ')})</span>
        </div>`,
        { direction: 'top', offset: [0, -10] }
      );

      marker.on('click', () => {
        onSelectLocation(loc);
        map.setView([loc.latitude, loc.longitude], 10, { animate: true });
      });

      markersRef.current.push(marker);
    });

    // Draw primary vulnerable road corridors (NH-37, NH-29, NH-06)
    const roads = [
      {
        name: 'NH-37 Noney Railway Corridor',
        coords: [[24.80, 93.15], [24.85, 93.40], [24.92, 93.60], [24.81, 93.92]],
        color: '#ef4444',
      },
      {
        name: 'NH-29 Kohima Ridge Highway',
        coords: [[25.90, 93.72], [25.75, 93.90], [25.66, 94.11]],
        color: '#f97316',
      },
    ];

    roads.forEach((road) => {
      const poly = L.polyline(road.coords, {
        color: road.color,
        weight: 3,
        dashArray: '5, 8',
        opacity: 0.7,
      }).addTo(map);
      poly.bindTooltip(road.name);
      markersRef.current.push(poly);
    });
  }, [locations, selectedLocation]);

  return (
    <div className={`relative w-full rounded-2xl overflow-hidden border border-slate-800 bg-command-card ${className}`}>
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Layer legend overlay */}
      <div className="absolute top-4 left-4 z-[500] p-3 rounded-xl bg-slate-900/90 backdrop-blur-md border border-slate-800 shadow-xl pointer-events-none">
        <div className="flex items-center gap-2 mb-2 font-bold text-xs text-slate-200">
          <Layers className="w-3.5 h-3.5 text-blue-400" />
          <span>NER Geohazard Layers</span>
        </div>
        <div className="space-y-1 text-[11px]">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500 animate-ping inline-block" />
            <span className="text-purple-300 font-semibold">Critical Risk Zones</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-400 inline-block" />
            <span className="text-red-300">Very High Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-400 inline-block" />
            <span className="text-orange-300">High Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-400 inline-block" />
            <span className="text-yellow-300">Moderate</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-green-400 inline-block" />
            <span className="text-green-300">Low Risk</span>
          </div>
        </div>
      </div>
    </div>
  );
};
