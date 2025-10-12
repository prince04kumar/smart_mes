// API Configuration for Smart Campus Application

// EC2 Backend URL
const API_BASE_URL = 'http://100.26.22.38:5000';

// Alternative: Use environment variable
// const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://100.26.22.38:5000';

export default API_BASE_URL;

// API Endpoints
export const API_ENDPOINTS = {
  // Auth
  LOGIN: `${API_BASE_URL}/login`,
  REGISTER: `${API_BASE_URL}/register`,
  PROFILE: `${API_BASE_URL}/profile`,
  
  // Document Processing
  ANALYZE_ID: `${API_BASE_URL}/analyze-id`,
  ANALYZE_WEBCAM: `${API_BASE_URL}/analyze-webcam`,
  SEND_NOTIFICATION: `${API_BASE_URL}/send-notification-email`,
  
  // Persons
  PERSONS: `${API_BASE_URL}/persons`,
  CREATE_PERSON: `${API_BASE_URL}/create-person`,
  
  // Health Check
  HEALTH: `${API_BASE_URL}/health`,
};
