// mobile-app/services/apiClient.js - Fixed for mobile device connection
import axios from 'axios';

// IMPORTANT: Replace 192.168.0.XXX with your actual computer's IP address
// Find it by running 'ipconfig' on Windows and looking for IPv4 Address
const COMPUTER_IP = '192.168.0.101'; // Replace with YOUR computer's IP

// Use your computer's IP address instead of localhost for mobile devices
const BASE_URL = __DEV__ ? `http://${COMPUTER_IP}:3000` : 'https://your-api-domain.com';

console.log(`🌐 API Base URL: ${BASE_URL}`);

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging and auth
apiClient.interceptors.request.use(
  (config) => {
    // Add user ID or auth token here
    config.headers['user-id'] = 'demo-user';
    
    // Debug logging
    if (__DEV__) {
      console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    if (__DEV__) {
      console.log(`✅ API Response: ${response.config.url} - ${response.status}`);
    }
    return response;
  },
  (error) => {
    console.error('❌ API Error:', error.response?.status, error.response?.data || error.message);
    
    if (error.response?.status === 401) {
      // Handle authentication errors
      console.log('🔒 Authentication required');
    } else if (error.response?.status >= 500) {
      // Handle server errors
      console.log('🔥 Server error occurred');
    } else if (error.code === 'NETWORK_ERROR' || error.code === 'ECONNREFUSED') {
      console.log(`📶 Network connection error - check if backend is running on ${BASE_URL}`);
    }
    
    return Promise.reject(error);
  }
);

// API helper functions
export const api = {
  // Garmin data endpoints
  getLatestMetrics: () => apiClient.get('/garmin/latest-metrics'),
  syncGarminData: () => apiClient.post('/garmin/sync'),
  getGarminStatus: () => apiClient.get('/garmin/status'),
  getWeeklySummary: () => apiClient.get('/garmin/weekly-summary'),
  
  // AI agent endpoints
  getDailyInsights: (data) => apiClient.post('/agent/analyze', {
    request_type: 'daily_insights',
    data: data
  }),
  chatWithAgent: (message, conversationHistory = []) => apiClient.post('/agent/chat', {
    message: message,
    conversation_history: conversationHistory
  }),
  
  // System endpoints
  checkHealth: () => apiClient.get('/health'),
  getSetupStatus: () => apiClient.get('/setup/garmindb-status'),
};

export default apiClient;