import React from 'react';
import { Alert } from '../../types';
import { RiskBadge } from './RiskBadge';
import { Bell, CheckCircle2, ShieldAlert } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface AlertCardProps {
  alert: Alert;
  onAcknowledge?: (id: number) => void;
}

export const AlertCard: React.FC<AlertCardProps> = ({ alert, onAcknowledge }) => {
  const isCritical = alert.risk_level === 'CRITICAL';

  return (
    <div
      className={`p-4 rounded-xl border transition-all duration-300 ${
        isCritical
          ? 'border-purple-500/50 bg-purple-950/20 shadow-[0_0_15px_rgba(168,85,247,0.15)] animate-glow-critical'
          : 'border-slate-800 bg-command-card/90 hover:border-slate-700'
      }`}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2">
          {isCritical ? (
            <ShieldAlert className="w-5 h-5 text-purple-400 shrink-0 animate-bounce" />
          ) : (
            <Bell className="w-4 h-4 text-orange-400 shrink-0" />
          )}
          <span className="font-bold text-sm text-slate-100">{alert.location_name || 'Regional Hazard Zone'}</span>
        </div>
        <RiskBadge level={alert.risk_level} size="sm" />
      </div>

      <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line mb-3 font-sans">
        {alert.message}
      </p>

      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800">
        <span>
          {alert.created_at ? formatDistanceToNow(new Date(alert.created_at), { addSuffix: true }) : 'Just now'}
        </span>
        {alert.acknowledged_at ? (
          <span className="inline-flex items-center gap-1 text-emerald-400 font-medium">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Acknowledged
          </span>
        ) : (
          onAcknowledge && (
            <button
              onClick={() => onAcknowledge(alert.id)}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-[10px] font-medium transition"
            >
              Acknowledge
            </button>
          )
        )}
      </div>
    </div>
  );
};
