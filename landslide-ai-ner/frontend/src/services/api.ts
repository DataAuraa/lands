import axios from 'axios';
import {
  Location,
  Prediction,
  WeatherData,
  SensorReading,
  Alert,
  FieldReport,
  DashboardSummary,
  User,
  ScenarioStep
} from '../types';

const client = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token if present
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Auth
  login: async (formData: FormData) => {
    const res = await client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return res.data;
  },
  getCurrentUser: async (): Promise<User> => {
    const res = await client.get('/auth/me');
    return res.data;
  },

  // Dashboard
  getSummary: async (): Promise<DashboardSummary> => {
    const res = await client.get('/dashboard/summary');
    return res.data;
  },
  getRiskTrend: async (hours = 24) => {
    const res = await client.get(`/dashboard/charts/risk-trend?hours=${hours}`);
    return res.data;
  },
  getRainfallTrend: async (hours = 24) => {
    const res = await client.get(`/dashboard/charts/rainfall-trend?hours=${hours}`);
    return res.data;
  },

  // Locations
  getLocations: async (): Promise<Location[]> => {
    const res = await client.get('/locations');
    return res.data;
  },
  getLocation: async (id: number): Promise<Location> => {
    const res = await client.get(`/locations/${id}`);
    return res.data;
  },

  // Weather
  getCurrentWeather: async (locationId: number): Promise<WeatherData> => {
    const res = await client.get(`/weather/current?location_id=${locationId}`);
    return res.data;
  },
  getWeatherForecast: async (locationId: number) => {
    const res = await client.get(`/weather/forecast?location_id=${locationId}`);
    return res.data;
  },
  getWeatherHistory: async (locationId: number, hours = 72) => {
    const res = await client.get(`/weather/history?location_id=${locationId}&hours=${hours}`);
    return res.data;
  },

  // Sensors
  getSensors: async (locationId?: number): Promise<SensorReading[]> => {
    const url = locationId ? `/sensors?location_id=${locationId}` : '/sensors';
    const res = await client.get(url);
    return res.data;
  },
  postSensorTelemetry: async (data: any) => {
    const res = await client.post('/sensors/data', data);
    return res.data;
  },

  // Risk / Predictions
  predictDirect: async (features: any): Promise<Prediction> => {
    const res = await client.post('/ml/predict', features);
    return res.data;
  },
  runLocationPrediction: async (locationId: number): Promise<Prediction> => {
    const res = await client.post(`/predictions/run?location_id=${locationId}`);
    return res.data;
  },
  getPredictionHistory: async (locationId: number) => {
    const res = await client.get(`/predictions?location_id=${locationId}`);
    return res.data;
  },
  getCurrentRisk: async () => {
    const res = await client.get('/risk/current');
    return res.data;
  },

  // Alerts
  getAlerts: async (active = true): Promise<Alert[]> => {
    const res = await client.get(`/alerts?active=${active}`);
    return res.data;
  },
  acknowledgeAlert: async (id: number) => {
    const res = await client.patch(`/alerts/${id}/acknowledge`, {});
    return res.data;
  },

  // Field Reports
  getReports: async (): Promise<FieldReport[]> => {
    const res = await client.get('/reports');
    return res.data;
  },
  submitReport: async (data: any): Promise<FieldReport> => {
    const res = await client.post('/reports', data);
    return res.data;
  },
  verifyReport: async (id: number, status: string) => {
    const res = await client.patch(`/reports/${id}`, { verification_status: status });
    return res.data;
  },

  // GIS Layers
  getRiskZonesGeoJSON: async () => {
    const res = await client.get('/gis/risk-zones');
    return res.data;
  },
  getSensorsGeoJSON: async () => {
    const res = await client.get('/gis/sensors');
    return res.data;
  },
  getLandslidesGeoJSON: async () => {
    const res = await client.get('/gis/landslides');
    return res.data;
  },
  getRoadsGeoJSON: async () => {
    const res = await client.get('/gis/roads');
    return res.data;
  },

  // Simulation
  getSimulationSteps: async (): Promise<ScenarioStep[]> => {
    const res = await client.get('/simulation/steps');
    return res.data;
  },
  getSimulationStep: async (step: number): Promise<ScenarioStep> => {
    const res = await client.get(`/simulation/step/${step}`);
    return res.data;
  },

  // Historical
  getHistoricalLandslides: async () => {
    const res = await client.get('/landslides');
    return res.data;
  },

  // Models
  getModels: async () => {
    const res = await client.get('/models');
    return res.data;
  },
  getActiveModels: async () => {
    const res = await client.get('/models/active');
    return res.data;
  },
  triggerTraining: async () => {
    const res = await client.post('/models/train');
    return res.data;
  }
};
