import React, { useEffect, useRef } from 'react';
import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl';
import Plot from 'react-plotly.js';
import { ViewState } from '@deck.gl/core';

interface DashboardBViewProps {
  viewState: ViewState;
  onViewStateChange: (params: { viewState: ViewState }) => void;
  layers: any[];
  mapboxToken: string;
  isLayerManagerOpen: boolean;
  isChatOpen: boolean;
}

const DashboardBView: React.FC<DashboardBViewProps> = ({
  viewState,
  onViewStateChange,
  layers,
  mapboxToken,
  isLayerManagerOpen,
  isChatOpen
}) => {
  const deckRef = useRef<any>(null);
  const mapRef = useRef<any>(null);
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
    <div className="dashboard-view dashboard-b">
      <div className="view-header">
        <h2>Analytics Dashboard</h2>
      </div>
      <div className="view-content">
        {/* Analytics Grid */}
        <div className="analytics-grid">
          <div className="chart-container large">
            <Plot
              data={[
                {
                  x: Array.from({ length: 20 }, (_, i) => i),
                  y: Array.from({ length: 20 }, () => Math.random() * 100),
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'Series A'
                },
                {
                  x: Array.from({ length: 20 }, (_, i) => i),
                  y: Array.from({ length: 20 }, () => Math.random() * 100),
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'Series B'
                }
              ]}
              layout={{ 
                title: 'Time Series Analysis',
                margin: { t: 30, r: 20, l: 40, b: 40 },
                height: 300,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
              }}
              config={{ responsive: true }}
            />
          </div>
          <div className="chart-container">
            <Plot
              data={[{
                type: 'bar',
                x: ['A', 'B', 'C', 'D'],
                y: [20, 14, 23, 25]
              }]}
              layout={{ 
                title: 'Category Distribution',
                margin: { t: 30, r: 20, l: 40, b: 40 },
                height: 250,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
              }}
              config={{ responsive: true }}
            />
          </div>
          <div className="chart-container">
            <Plot
              data={[{
                values: [19, 26, 55],
                labels: ['Category A', 'Category B', 'Category C'],
                type: 'pie'
              }]}
              layout={{ 
                title: 'Distribution',
                margin: { t: 30, r: 20, l: 20, b: 20 },
                height: 250,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
              }}
              config={{ responsive: true }}
            />
          </div>
        </div>

        {/* Small Map Section */}
        <div className="secondary-map-section">
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
                mapStyle="mapbox://styles/mapbox/dark-v10"
              />
            </DeckGL>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardBView; 