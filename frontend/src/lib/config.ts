/**
 * Application configuration constants
 */

// Backend API Base URL
// Use environment variable if set, otherwise detect based on dev mode
export const API_BASE_URL = 
  import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.DEV 
    ? "http://localhost:8000"  // Development mode
    : "https://credit-backend-558345680759.us-west2.run.app"  // Production mode
  );
