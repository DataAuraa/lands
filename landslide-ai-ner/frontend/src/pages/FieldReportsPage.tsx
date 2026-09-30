import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { FieldReport, Location } from '../types';
import { FileText, Plus, CheckCircle, XCircle, MapPin, Send, AlertTriangle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export const FieldReportsPage: React.FC = () => {
  const [reports, setReports] = useState<FieldReport[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [reportType, setReportType] = useState('Crack');
  const [severity, setSeverity] = useState('medium');
  const [description, setDescription] = useState('');
  const [locationId, setLocationId] = useState<number>(2);

  useEffect(() => {
    api.getReports().then((res) => setReports(res));
    api.getLocations().then((res) => {
      setLocations(res);
      if (res.length > 0) setLocationId(res[0].id);
    });
  }, []);

  const handleVerify = async (id: number, status: string) => {
    try {
      await api.verifyReport(id, status);
      setReports((prev) =>
        prev.map((r) => (r.id === id ? { ...r, verification_status: status as any } : r))
      );
    } catch (e) {
      console.error(e);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const loc = locations.find((l) => l.id === locationId);
    try {
      const newReport = await api.submitReport({
        location_id: locationId,
        latitude: loc?.latitude ?? 24.92,
        longitude: loc?.longitude ?? 93.59,
        report_type: reportType,
        description,
        severity,
      });
      setReports([newReport, ...reports]);
      setShowSubmitModal(false);
      setDescription('');
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title & Submit report button */}
      <div className="p-4 rounded-xl border border-slate-800 bg-command-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-400" />
            Field Inspections & Citizen Geohazard Reports
          </h1>
          <p className="text-xs text-slate-400">
            Ground-truth crack observations, slope creep, and road blockage reports
          </p>
        </div>

        <button
          onClick={() => setShowSubmitModal(true)}
          className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center gap-2 transition shadow-lg shadow-blue-600/30"
        >
          <Plus className="w-4 h-4" />
          <span>Submit Field Report</span>
        </button>
      </div>

      {/* Reports Feed */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {reports.map((r) => {
          const isVerified = r.verification_status === 'VERIFIED';
          const isPending = r.verification_status === 'PENDING';

          return (
            <div
              key={r.id}
              className="p-4 rounded-xl border border-slate-800 bg-command-card/90 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div>
                    <span className="text-xs font-bold text-slate-200">{r.report_type.replace('_', ' ')}</span>
                    <div className="text-[11px] text-slate-400 flex items-center gap-1 mt-0.5">
                      <MapPin className="w-3 h-3 text-blue-400" />
                      <span>{r.location_name || 'Regional Slope'}</span>
                    </div>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      isVerified
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : isPending
                        ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        : 'bg-red-500/20 text-red-400 border border-red-500/30'
                    }`}
                  >
                    {r.verification_status}
                  </span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed mb-3">{r.description}</p>
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
                <span>By: {r.reporter_name || 'Field Officer Rongmei'}</span>
                {isPending && (
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => handleVerify(r.id, 'VERIFIED')}
                      className="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-[10px] flex items-center gap-1"
                    >
                      <CheckCircle className="w-3 h-3" />
                      Verify
                    </button>
                    <button
                      onClick={() => handleVerify(r.id, 'REJECTED')}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-rose-900/40 text-rose-400 text-[10px] font-semibold flex items-center gap-1 border border-slate-700"
                    >
                      <XCircle className="w-3 h-3" />
                      Reject
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Submit Report Modal */}
      {showSubmitModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-[1000] flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl">
            <h3 className="font-bold text-base text-slate-100 mb-4 flex items-center gap-2">
              <Send className="w-5 h-5 text-blue-400" />
              Submit Field Geohazard Observation
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Observed Hazard Type</label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200"
                >
                  <option value="Crack">Crown / Road-cut Tension Crack</option>
                  <option value="Slope_Movement">Hillside Creep Movement</option>
                  <option value="Rockfall">Boulder Fall / Rockfall</option>
                  <option value="Landslide">Active Debris Slide</option>
                  <option value="Road_Blockage">Corridor Road Blockage</option>
                  <option value="Drainage_Failure">Toe Erosion / Culvert Failure</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Monitored Zone</label>
                <select
                  value={locationId}
                  onChange={(e) => setLocationId(Number(e.target.value))}
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
                <label className="text-xs font-semibold text-slate-300 block mb-1">Severity Assessment</label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200"
                >
                  <option value="low">Low (Minor debris / hairline crack)</option>
                  <option value="medium">Medium (Traffic restricted)</option>
                  <option value="high">High (Severe structural tension crack)</option>
                  <option value="critical">Critical (Imminent slope failure)</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Field Description</label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe crack length, depth, water seepage, or tilt of utility poles..."
                  className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowSubmitModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs text-white font-bold"
                >
                  Submit Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
