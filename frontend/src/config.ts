const getApiBaseUrl = () => {
  // In production, use relative path as Nginx handles the proxy
  if (import.meta.env.PROD) {
    return '/api';
  }
  // In development, use the full URL from environment
  return `${import.meta.env.VITE_BACKEND_URL}/api`;
};

export const config = {
    API_BASE_URL: getApiBaseUrl(),
    MAPBOX_TOKEN: import.meta.env.VITE_MAPBOX_ACCESS_TOKEN,
    // Add health check endpoint
    HEALTH_CHECK_URL: `${getApiBaseUrl()}/health`
}; 