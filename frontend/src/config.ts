const getApiBaseUrl = () => {
  // In production, use relative path as Nginx handles the proxy
  if (import.meta.env.PROD) {
    return '/api';
  }
  // In development, use the full URL from environment
  return `${import.meta.env.VITE_BACKEND_URL}/api`;
};

// Get the base URL without the /api suffix for direct endpoints
const getBaseUrl = () => {
  if (import.meta.env.PROD) {
    return ''; // Empty string for relative URLs in production
  }
  return import.meta.env.VITE_BACKEND_URL;
};

export const config = {
    API_BASE_URL: getApiBaseUrl(),
    MAPBOX_TOKEN: import.meta.env.VITE_MAPBOX_ACCESS_TOKEN,
    // Primary health check URL (with /api prefix)
    HEALTH_CHECK_URL: `${getApiBaseUrl()}/health`,
    // Fallback health check URL (direct /health endpoint)
    HEALTH_CHECK_FALLBACK_URL: `${getBaseUrl()}/health`
}; 