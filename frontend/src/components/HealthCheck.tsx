import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { config } from '../config';

interface HealthStatus {
  status: string;
  service: string;
}

export const HealthCheck: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await axios.get(config.HEALTH_CHECK_URL);
        setHealth(response.data);
        setError(null);
      } catch (err) {
        setError('Backend service unavailable');
        setHealth(null);
      }
    };

    // Check immediately
    checkHealth();

    // Then check every 30 seconds
    const interval = setInterval(checkHealth, 30000);

    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div style={{ 
        position: 'fixed', 
        bottom: 10, 
        right: 10, 
        padding: '8px 16px',
        backgroundColor: '#ff4d4f',
        color: 'white',
        borderRadius: 4,
        zIndex: 1000
      }}>
        {error}
      </div>
    );
  }

  if (health?.status !== 'healthy') {
    return (
      <div style={{ 
        position: 'fixed', 
        bottom: 10, 
        right: 10, 
        padding: '8px 16px',
        backgroundColor: '#faad14',
        color: 'white',
        borderRadius: 4,
        zIndex: 1000
      }}>
        Service Status: {health?.status || 'Unknown'}
      </div>
    );
  }

  return null;
}; 