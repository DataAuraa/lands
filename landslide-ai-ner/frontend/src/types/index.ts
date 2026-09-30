export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'VERY_HIGH' | 'CRITICAL';
export type SensorStatus = 'ONLINE' | 'OFFLINE' | 'LOW_BATTERY' | 'ERROR';
export type UserRole = 'admin' | 'district_admin' | 'dma' | 'field_officer' | 'citizen';
export type ReportType = 'Crack' | 'Slope_Movement' | 'Rockfall' | 'Landslide' | 'Road_Blockage' | 'Flooding' | 'Drainage_Failure' | 'Other';
export type VerificationStatus = 'PENDING' | 'VERIFIED' | 'REJECTED';

export interface Location {
  id: number;
  name: string;
  state: string;
  district: string;
  block?: string;
  village?: string;
  latitude: number;
  longitude: number;
  elevation: number;
  slope: number;
  aspect?: number;
  population?: number;
  road_connectivity?: string;
  infrastructure_type?: string;
  land_cover?: string;
  geology?: string;
  distance_to_road?: number;
  distance_to_river?: number;
  is_active: boolean;
  latest_risk_score?: number;
  latest_risk_level?: RiskLevel;
}

export interface Prediction {
  risk_score: number;
  risk_level: RiskLevel;
  probability: number;
  model_version: string;
  confidence: number;
  top_factors: string[];
  explanation?: Record<string, any>;
  sub_scores?: Record<string, number>;
  timestamp?: string;
  location_id?: number;
  location_name?: string;
  disclaimer: string;
}

export interface WeatherData {
  station_id: string;
  latitude: number;
  longitude: number;
  timestamp: string;
  rainfall_1h: number;
  rainfall_3h: number;
  rainfall_6h: number;
  rainfall_12h: number;
  rainfall_24h: number;
  rainfall_72h: number;
  temperature: number;
  humidity: number;
  wind_speed: number;
  pressure: number;
  source: string;
  is_simulation?: boolean;
}

export interface SensorReading {
  id: number;
  sensor_id: string;
  location_id: number;
  name: string;
  latitude: number;
  longitude: number;
  is_active: boolean;
  latest_soil_moisture?: number;
  latest_status?: SensorStatus;
  latest_battery?: number;
  last_seen?: string;
}

export interface Alert {
  id: number;
  location_id: number;
  location_name?: string;
  alert_type: string;
  risk_level: RiskLevel;
  message: string;
  language: string;
  created_at: string;
  expires_at?: string;
  delivery_status: string;
  recipient_count: number;
  is_active: boolean;
  acknowledged_by?: number;
  acknowledged_at?: string;
}

export interface FieldReport {
  id: number;
  user_id: number;
  reporter_name?: string;
  location_id?: number;
  location_name?: string;
  latitude: number;
  longitude: number;
  report_type: ReportType;
  description: string;
  image_url?: string;
  video_url?: string;
  severity: string;
  timestamp: string;
  verification_status: VerificationStatus;
  verified_by?: number;
  verified_at?: string;
}

export interface DashboardSummary {
  total_locations: number;
  active_sensors: number;
  sensors_online: number;
  sensors_offline: number;
  sensors_warning: number;
  low_risk_count: number;
  moderate_risk_count: number;
  high_risk_count: number;
  very_high_risk_count: number;
  critical_risk_count: number;
  active_alerts: number;
  open_incidents: number;
  blocked_roads: number;
  risk_distribution: Record<string, number>;
  system_status: Record<string, string>;
  recent_alerts: Alert[];
  recent_reports: FieldReport[];
  simulation_mode: boolean;
  model_version: string;
  last_updated: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
  phone?: string;
  role: UserRole;
  district?: string;
  state?: string;
  preferred_language: string;
}

export interface ScenarioStep {
  step: number;
  title: string;
  description: string;
  rainfall_1h: number;
  rainfall_24h: number;
  soil_moisture: number;
  risk_score: number;
  risk_level: RiskLevel;
  action: string;
}
