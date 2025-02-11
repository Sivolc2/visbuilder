import React, { useState, useEffect } from 'react';
import './App.css';
import DynamicView from './components/DynamicView';
import { HealthCheck } from './components/HealthCheck';
import axios from 'axios';
import { config } from './config';

interface View {
  id: string;
  config: {
    name: string;
    type: string;
    description: string;
  };
}

interface ViewsResponse {
  [key: string]: View;
}

function App() {
  const [views, setViews] = useState<View[]>([]);
  const [selectedViewId, setSelectedViewId] = useState<string>('');

  const fetchViews = async () => {
    try {
      const response = await axios.get<ViewsResponse>(`${config.API_BASE_URL}/api/views`);
      const viewsData = Object.values(response.data);
      setViews(viewsData);
      
      // Select the first view by default if none is selected
      if (viewsData.length > 0 && !selectedViewId) {
        setSelectedViewId(viewsData[0].id);
      }
    } catch (error) {
      console.error('Error fetching views:', error);
    }
  };

  useEffect(() => {
    fetchViews();
    // Refresh views every 30 seconds
    const interval = setInterval(fetchViews, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <select 
          value={selectedViewId} 
          onChange={(e) => setSelectedViewId(e.target.value)}
          className="view-selector"
        >
          <option value="">Select a view</option>
          {views.map((view) => (
            <option key={view.id} value={view.id}>
              {view.config.name}
            </option>
          ))}
        </select>
      </header>
      <main>
        {selectedViewId && (
          <DynamicView 
            viewId={selectedViewId} 
            mapboxToken={config.MAPBOX_TOKEN}
          />
        )}
      </main>
      <HealthCheck />
    </div>
  );
}

export default App; 