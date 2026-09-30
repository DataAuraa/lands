import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Location, Prediction, Alert, SensorReading } from '../types';
import { StatCard } from '../components/ui/StatCard';
import { AlertCard } from '../components/ui/AlertCard';
import { SensorStatusCard } from '../components/ui/SensorStatusCard';
import { RiskMap } from '../components/map/RiskMap';
import { LocationDetailPanel } from '../components/map/LocationDetailPanel';
import { RainfallChart } from '../components/dashboard/RainfallChart';
import { RiskTrendChart } from '../components/dashboard/RiskTrendChart';
import { SimulationPanel } from '../components/dashboard/SimulationPanel';
import {
  Mountain,
  AlertTriangle,
  Cpu,
  Bell,
  ShieldCheck,
  Radio,
  FileText,
  Activity,
  Car
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const [locations, setLocations] = useState<Location[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [sensors, setSensors] = useState<SensorReading[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [selectedPrediction, setSelectedPrediction] = useState<Prediction | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [locsRes, alertsRes, sensorsRes] = await Promise.all([
          api.getLocations(),
          api.getAlerts(true),
          api.getSensors(),
        ]);
        setLocations(locsRes);
        setAlerts(alertsRes);
        setSensors(sensorsRes);
        if (locsRes.length > 0) {
          // Default selection: Noney Tupul (site of interest)
          const noney = locsRes.find((l) => l.name.toLowerCase().includes('noney')) || locsRes[0];
          setSelectedLocation(noney);
        }
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleSelectLocation = async (loc: Location) => {
    setSelectedLocation(loc);
    try {
      const pred = await api.runLocationPrediction(loc.id);
      setSelectedPrediction(pred);
    } catch {
      // fallback
    }
  };

  const handleAcknowledgeAlert = async (alertId: number) => {
    try {
      await api.acknowledgeAlert(alertId);
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, acknowledged_at: new Date().toISOString() } : a))
      );
    } catch (e) {
      console.error(e);
    }
  };

  const criticalCount = locations.filter((l) => l.latest_risk_level === 'CRITICAL').length;
  const highRiskCount = locations.filter((l) => l.latest_risk_level === 'HIGH' || l.latest_risk_level === 'VERY_HIGH').length;

  return (
    <div className="space-y-6">
      {/* Top Telemetry KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <StatCard
          title="Monitored Zones"
          value={locations.length || 12}
          subtitle="Across 6 NER States"
          icon={Mountain}
          color="blue"
        />
        <StatCard
          title="Critical Zones"
          value={criticalCount || 1}
          subtitle="Immediate Action"
          icon={AlertTriangle}
          color="purple"
          trend="Noney Yard"
        />
        <StatCard
          title="High Risk Slopes"
          value={highRiskCount || 3}
          subtitle="Slope Saturation >75%"
          icon={Activity}
          color="red"
        />
        <StatCard
          title="IoT Sensors Online"
          value={`${sensors.filter((s) => s.latest_status !== 'OFFLINE').length || 11}/${sensors.length || 12}`}
          subtitle="Piezometers & Nodes"
          icon={Cpu}
          color="green"
        />
        <StatCard
          title="Active Alerts"
          value={alerts.length || 2}
          subtitle="Broadcast to DEOC"
          icon={Bell}
          color="yellow"
        />
        <StatCard
          title="Corridor Closures"
          value="2"
          subtitle="NH-37 & NH-06 cuts"
          icon={Car}
          color="red"
        />
      </div>

      {/* Primary Command Center View: Left 65% GIS Map, Right 35% Live Feeds */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: GIS Map */}
        <div className="lg:col-span-8 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-pulse" />
                Live Regional Geospatial Risk Map
              </h2>
              <p className="text-xs text-slate-400">Click any monitored slope zone to inspect geotechnical parameters</p>
            </div>
            <span className="text-xs font-mono text-slate-400 bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
              WGS-84 (SRID 4326)
            </span>
          </div>

          <RiskMap
            locations={locations}
            selectedLocation={selectedLocation}
            onSelectLocation={handleSelectLocation}
            className="h-[480px]"
          />
        </div>

        {/* Right: Active Emergency Bulletins & Sensor Health */}
        <div className="lg:col-span-4 space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                <Bell className="w-4 h-4 text-purple-400" />
                Emergency Bulletins ({alerts.length})
              </h3>
              <span className="text-[10px] text-slate-500 font-mono">BROADCAST FEED</span>
            </div>

            <div className="space-y-2.5 max-h-[220px] overflow-y-auto pr-1">
              {alerts.length > 0 ? (
                alerts.map((alert) => (
                  <AlertCard
                    key={alert.id}
                    alert={alert}
                    onAcknowledge={handleAcknowledgeAlert}
                  />
                ))
              ) : (
                <div className="p-4 rounded-xl border border-slate-800 text-center text-xs text-slate-500">
                  No active emergency alerts at this time.
                </div>
              )}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-blue-400" />
                IoT Soil Telemetry Feed
              </h3>
              <span className="text-[10px] text-slate-500 font-mono">ESP32 / LORAWAN</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-2 max-h-[220px] overflow-y-auto pr-1">
              {sensors.slice(0, 4).map((sensor) => (
                <SensorStatusCard
                  key={sensor.sensor_id}
                  sensor={sensor}
                  onClick={() => {
                    const loc = locations.find((l) => l.id === sensor.location_id);
                    if (loc) handleSelectLocation(loc);
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 12-Step Primary Demonstration Stepper */}
      <SimulationPanel />

      {/* Analytical Telemetry Charts (Rainfall vs Risk Trajectory) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RainfallChart />
        <RiskTrendChart />
      </div>

      {/* Slide-in Detail Panel when a location is selected */}
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
