import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useDashboardStore } from '../../store/dashboardStore';
import {
  ShieldAlert,
  LayoutDashboard,
  MapPin,
  LineChart,
  CloudRain,
  Cpu,
  FileText,
  Bell,
  CpuIcon,
  Globe,
  LogOut,
  User as UserIcon,
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuthStore();
  const { activeLanguage, setLanguage } = useDashboardStore();

  const navLinks = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Live GIS Map', path: '/map', icon: MapPin },
    { name: 'AI Risk Engine', path: '/risk-analysis', icon: LineChart },
    { name: 'Precipitation', path: '/weather', icon: CloudRain },
    { name: 'IoT Sensors', path: '/sensors', icon: Cpu },
    { name: 'Field Reports', path: '/reports', icon: FileText },
    { name: 'Emergency Alerts', path: '/alerts', icon: Bell },
  ];

  return (
    <header className="bg-command-card/90 border-b border-slate-800 sticky top-0 z-[600] backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
        {/* Left: Brand / Title */}
        <Link to="/" className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="font-extrabold text-sm sm:text-base tracking-tight text-white flex items-center gap-2">
              <span>LANDSLIDE EARLY WARNING SYSTEM</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                NER-AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Northeast India Geohazard Command Center</p>
          </div>
        </Link>

        {/* Center: Desktop Nav Links */}
        <nav className="hidden lg:flex items-center gap-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.path;
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                  isActive
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Right: Language + User Profile */}
        <div className="flex items-center gap-3">
          {/* Multilingual Selector */}
          <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded-lg px-2 py-1 text-xs">
            <Globe className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={activeLanguage}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-transparent text-slate-300 text-xs focus:outline-none cursor-pointer"
            >
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="as">অসমীয়া (Assamese)</option>
              <option value="bn">বাংলা (Bengali)</option>
            </select>
          </div>

          {/* User Profile */}
          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <div className="text-right hidden sm:block">
                <div className="text-xs font-bold text-slate-200">{user?.name || 'Authorized Officer'}</div>
                <div className="text-[10px] font-mono text-blue-400 uppercase">{user?.role || 'OFFICER'}</div>
              </div>
              <button
                onClick={logout}
                className="p-2 rounded-lg bg-slate-800 hover:bg-red-500/20 hover:text-red-400 text-slate-400 border border-slate-700 transition"
                title="Sign Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition shadow-md shadow-blue-600/20 flex items-center gap-1.5"
            >
              <UserIcon className="w-3.5 h-3.5" />
              <span>Login</span>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};
