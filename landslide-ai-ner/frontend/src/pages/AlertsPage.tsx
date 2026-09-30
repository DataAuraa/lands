import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Alert, Location } from '../types';
import { AlertCard } from '../components/ui/AlertCard';
import { Bell, Plus, ShieldAlert, CheckCircle2 } from 'lucide-react';

export const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedLocId, setSelectedLocId] = useState<number>(2);
  const [riskLevel, setRiskLevel] = useState<string>('HIGH');
  const [message, setMessage] = useState<string>('');

  useEffect(() => {
    api.getAlerts(false).then((res) => setAlerts(res));
    api.getLocations().then((res) => {
      setLocations(res);
      if (res.length > 0) setSelectedLocId(res[0].id);
    });
  }, []);

  const handleAcknowledge = async (id: number) => {
    try {
      await api.acknowledgeAlert(id);
      setAlerts((prev) =>
        prev.map((a) => (a.id === id ? { ...a, acknowledged_at: new Date().toISOString() } : a))
      );
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.predictDirect({
        rainfall_24h: 180,
        soil_moisture: 88,
        slope: 38,
        elevation: 850,
      });
      setShowCreateModal(false);
      const updated = await api.getAlerts(false);
      setAlerts(updated);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title & Create button */}
      <div className="p-4 rounded-xl border border-slate-800 bg-command-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Bell className="w-5 h-5 text-purple-400" />
            Emergency Disaster Warnings & Bulletins
          </h1>
          <p className="text-xs text-slate-400">
            Automated AI triggers and authority broadcast bulletins for Northeast India
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs flex items-center gap-2 transition shadow-lg shadow-purple-600/30"
        >
          <Plus className="w-4 h-4" />
          <span>Broadcast Warning</span>
        </button>
      </div>

      {/* Alert Feed */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {alerts.map((alert) => (
          <AlertCard
            key={alert.id}
            alert={alert}
            onAcknowledge={handleAcknowledge}
          />
        ))}
      </div>

      {/* Create Alert Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-[1000] flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center gap-2 mb-4">
              <ShieldAlert className="w-5 h-5 text-purple-400" />
              <h3 className="font-bold text-base text-slate-100">Issue Emergency Broadcast</h3>
            </div>

            <form onSubmit={handleCreateAlert} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Target Geozone</label>
                <select
                  value={selectedLocId}
                  onChange={(e) => setSelectedLocId(Number(e.target.value))}
                  className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200"
                >
                  {locations.map((loc) => (
                    <option key={loc.id} value={loc.id}>
                      {loc.name} ({loc.district}, {loc.state})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Risk Severity Tier</label>
                <select
                  value={riskLevel}
                  onChange={(e) => setRiskLevel(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200"
                >
                  <option value="HIGH">HIGH RISK</option>
                  <option value="VERY_HIGH">VERY HIGH RISK</option>
                  <option value="CRITICAL">CRITICAL RISK</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Broadcast Directive Message</label>
                <textarea
                  rows={3}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Enter evacuation guidance or road closure instructions..."
                  className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-xs text-white font-bold"
                >
                  Dispatch Bulletin
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
