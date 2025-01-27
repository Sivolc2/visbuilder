import React, { useEffect, useRef } from 'react';
import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl';
import Plot from 'react-plotly.js';
import { ViewState } from '@deck.gl/core';
import { LineLayer } from '@deck.gl/layers';

interface DashboardAViewProps {
  viewState: ViewState;
  onViewStateChange: (params: { viewState: ViewState }) => void;
  layers: any[];
  mapboxToken: string;
  isLayerManagerOpen: boolean;
  isChatOpen: boolean;
}

const DashboardAView: React.FC<DashboardAViewProps> = ({
  viewState,
  onViewStateChange,
  layers,
  mapboxToken,
  isLayerManagerOpen,
  isChatOpen
}) => {
  const mapRef = useRef<any>(null);
  const deckRef = useRef<any>(null);
  const resizeTimeoutRef = useRef<number | null>(null);

  // Handle resize when panels toggle or window resizes
  useEffect(() => {
    const handleResize = () => {
      if (resizeTimeoutRef.current) {
        window.clearTimeout(resizeTimeoutRef.current);
      }

      // Force a re-render to trigger DeckGL resize
      if (deckRef.current) {
        const width = deckRef.current.parentElement.clientWidth;
        const height = deckRef.current.parentElement.clientHeight;
        deckRef.current.style.width = `${width}px`;
        deckRef.current.style.height = `${height}px`;
      }

      // Resize the Mapbox map
      if (mapRef.current) {
        mapRef.current.resize();
      }

      // Set a delayed resize for after animation
      resizeTimeoutRef.current = window.setTimeout(() => {
        if (deckRef.current) {
          const width = deckRef.current.parentElement.clientWidth;
          const height = deckRef.current.parentElement.clientHeight;
          deckRef.current.style.width = `${width}px`;
          deckRef.current.style.height = `${height}px`;
        }
        // Resize the Mapbox map again after animation
        if (mapRef.current) {
          mapRef.current.resize();
        }
        resizeTimeoutRef.current = null;
      }, 300);
    };

    // Initial resize
    handleResize();

    // Add window resize listener
    const windowResizeHandler = () => {
      handleResize();
    };
    window.addEventListener('resize', windowResizeHandler);

    return () => {
      window.removeEventListener('resize', windowResizeHandler);
      if (resizeTimeoutRef.current) {
        window.clearTimeout(resizeTimeoutRef.current);
      }
    };
  }, [isLayerManagerOpen, isChatOpen]);

  return (
    <div className="dashboard-view dashboard-a">
      <div className="view-header">
        <h2>Geospatial Analysis Dashboard</h2>
      </div>
      <div className="view-content">
        {/* Large map section */}
        <div className="primary-map-section">
          <div ref={deckRef} style={{ width: '100%', height: '100%' }}>
            <DeckGL
              viewState={viewState}
              controller={true}
              layers={layers}
              onViewStateChange={onViewStateChange}
            >
              <Map
                ref={mapRef}
                reuseMaps
                mapboxAccessToken={mapboxToken}
                mapStyle="mapbox://styles/mapbox/light-v10"
              />
            </DeckGL>
          </div>
        </div>
        
        {/* Metrics and Charts Section */}
        <div className="metrics-and-charts">
          <div className="metrics-row">
            <div className="metric-card">
              <h3>Active Layers</h3>
              <div className="metric-value">{layers.length}</div>
            </div>
            <div className="metric-card">
              <h3>Current Zoom</h3>
              <div className="metric-value">{viewState.zoom.toFixed(1)}</div>
            </div>
          </div>
          <div className="charts-row">
            <div className="chart-card">
              <Plot
                data={[{ x: [1, 2, 3], y: [2, 6, 3], type: 'scatter', mode: 'lines+markers' }]}
                layout={{ 
                  title: 'Time Series',
                  margin: { t: 30, r: 20, l: 40, b: 40 },
                  height: 250,
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  plot_bgcolor: 'rgba(0,0,0,0)',
                }}
                config={{ responsive: true, displayModeBar: false }}
              />
            </div>
            <div className="chart-card">
              <Plot
                data={[{ values: [19, 26, 55], labels: ['A', 'B', 'C'], type: 'pie' }]}
                layout={{ 
                  title: 'Distribution',
                  margin: { t: 30, r: 20, l: 20, b: 20 },
                  height: 250,
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  plot_bgcolor: 'rgba(0,0,0,0)',
                  showlegend: false
                }}
                config={{ responsive: true, displayModeBar: false }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardAView; 