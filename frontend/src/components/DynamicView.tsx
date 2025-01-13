import React, { useEffect, useState, useCallback, useRef } from 'react';
import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl';
import Plot from 'react-plotly.js';
import { ViewState } from '@deck.gl/core';
import { LineLayer } from '@deck.gl/layers';
import { HexagonLayer } from '@deck.gl/aggregation-layers';
import { HeatmapLayer } from '@deck.gl/aggregation-layers';
import { ScatterplotLayer } from '@deck.gl/layers';
import axios from 'axios';
import { config } from '../config';
import LayerManager from './LayerManager';
import { FilterDefinition } from '../services/dataService';

interface ViewConfig {
  id: string;
  config: {
    name: string;
    type: string;
    description: string;
    data_sources: any[];
    components: any[];
    settings: {
      refresh_rate: number;
      default_zoom: number;
      center: [number, number];
      time_window: number;
    };
  };
  last_updated: number;
}

interface DynamicViewProps {
  viewId: string;
  mapboxToken: string;
}

interface LayerState {
  id: string;
  name: string;
  type: string;
  data_source: string;
  visible: boolean;
  filters: FilterDefinition[];
  properties: Record<string, any>;
}

const DynamicView: React.FC<DynamicViewProps> = ({ viewId, mapboxToken }) => {
  const [viewConfig, setViewConfig] = useState<ViewConfig | null>(null);
  const [viewState, setViewState] = useState<ViewState>({
    longitude: 0,
    latitude: 0,
    zoom: 1,
    pitch: 0,
    bearing: 0
  });
  const [layerData, setLayerData] = useState<Record<string, any>>({});
  const [visualizationData, setVisualizationData] = useState<Record<string, any>>({});
  const [layers, setLayers] = useState<LayerState[]>([]);
  const mapRef = useRef<any>(null);

  const fetchViewConfig = async () => {
    try {
      console.log('Fetching view config for viewId:', viewId);
      const response = await axios.get<ViewConfig>(`${config.API_BASE_URL}/api/views/${viewId}`);
      console.log('Received view config:', response.data);
      setViewConfig(response.data);
      
      if (response.data?.config?.settings) {
        const { center, default_zoom } = response.data.config.settings;
        setViewState({
          longitude: center[0],
          latitude: center[1],
          zoom: default_zoom,
          pitch: 0,
          bearing: 0
        });
      }
    } catch (error) {
      console.error('Error fetching view config:', error);
    }
  };

  useEffect(() => {
    if (viewId) {
      fetchViewConfig();
    }
  }, [viewId]);

  const fetchLayerData = async (layer: LayerState) => {
    try {
      const response = await axios.post(
        `${config.API_BASE_URL}/api/data/${layer.data_source}/filtered`,
        { filters: layer.filters }
      );
      setLayerData(prev => ({
        ...prev,
        [layer.id]: response.data
      }));
    } catch (error) {
      console.error(`Error fetching data for layer ${layer.id}:`, error);
    }
  };

  useEffect(() => {
    const fetchAllData = async () => {
      for (const layer of layers) {
        if (layer.visible) {
          await fetchLayerData(layer);
        }
      }
    };
    fetchAllData();
  }, [layers]);

  useEffect(() => {
    if (viewConfig) {
      const initialLayers = viewConfig.config.components
        .filter(comp => comp.type === 'map')
        .flatMap(comp => comp.layers.map(layer => ({
          id: layer.id,
          name: layer.name || layer.id,
          type: layer.type,
          data_source: layer.data_source,
          visible: true,
          filters: [],
          properties: layer.properties
        })));
      setLayers(initialLayers);
    }
  }, [viewConfig]);

  const handleLayerVisibilityChange = (layerId: string, visible: boolean) => {
    setLayers(prevLayers =>
      prevLayers.map(layer =>
        layer.id === layerId ? { ...layer, visible } : layer
      )
    );
  };

  const handleLayerFiltersChange = (layerId: string, filters: FilterDefinition[]) => {
    setLayers(prevLayers =>
      prevLayers.map(layer =>
        layer.id === layerId ? { ...layer, filters } : layer
      )
    );
  };

  const getDeckLayers = () => {
    if (!viewConfig) return [];

    return layers
      .filter(layer => layer.visible)
      .map(layer => {
        const data = layerData[layer.id] || [];
        
        switch (layer.type) {
          case 'line':
            return new LineLayer({
              id: layer.id,
              data,
              ...layer.properties
            });
          case 'heatmap':
            return new HeatmapLayer({
              id: layer.id,
              data,
              ...layer.properties
            });
          case 'hexagon':
            return new HexagonLayer({
              id: layer.id,
              data,
              ...layer.properties
            });
          case 'scatterplot':
            return new ScatterplotLayer({
              id: layer.id,
              data,
              ...layer.properties
            });
          default:
            return null;
        }
      })
      .filter(Boolean);
  };

  const fetchVisualizationData = async () => {
    if (!viewConfig) return;

    try {
      const visualizations = viewConfig.config.components
        .filter(comp => comp.type === 'grid')
        .flatMap(comp => comp.visualizations);

      for (const vis of visualizations) {
        try {
          const response = await axios.get(`${config.API_BASE_URL}/api/data/${vis.data_source}`);
          const sourceData = response.data;

          if (vis.type === 'line') {
            const timestamps = sourceData?.timestamps || [];
            const volume = sourceData?.volume || [];
            setVisualizationData(prev => ({
              ...prev,
              [vis.id]: {
                x: timestamps,
                y: volume
              }
            }));
          } else if (vis.type === 'pie') {
            if (!vis.properties?.values || !Array.isArray(vis.properties.values)) {
              console.warn(`Invalid values configuration for visualization ${vis.id}`);
              continue;
            }

            const values = vis.properties.values.map((path: string) => {
              try {
                const keys = path.split('.');
                let value = sourceData;
                for (const key of keys) {
                  if (value === undefined || value === null) return 0;
                  value = value[key];
                }
                return value || 0;
              } catch (error) {
                console.warn(`Error extracting value for path ${path}:`, error);
                return 0;
              }
            });

            setVisualizationData(prev => ({
              ...prev,
              [vis.id]: {
                values,
                labels: vis.properties?.labels || values.map((_, i) => `Value ${i + 1}`)
              }
            }));
          }
        } catch (error) {
          console.error(`Error fetching data for visualization ${vis.id}:`, error);
        }
      }
    } catch (error) {
      console.error('Error processing visualization data:', error);
    }
  };

  useEffect(() => {
    if (viewId) {
      fetchViewConfig();
    }
  }, [viewId]);

  useEffect(() => {
    if (viewConfig) {
      fetchVisualizationData();
      const interval = setInterval(
        fetchVisualizationData,
        viewConfig.config.settings.refresh_rate * 1000
      );
      return () => clearInterval(interval);
    }
  }, [viewConfig]);

  if (!viewConfig || !viewState) {
    console.log('Still loading:', { viewConfig, viewState });
    return <div>Loading...</div>;
  }

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <DeckGL
        viewState={viewState}
        onViewStateChange={({ viewState }) => setViewState(viewState)}
        controller={true}
        layers={getDeckLayers()}
      >
        <Map
          ref={mapRef}
          mapboxAccessToken={mapboxToken}
          mapStyle="mapbox://styles/mapbox/dark-v10"
        />
      </DeckGL>
      <div style={{ position: 'absolute', top: 20, right: 20, zIndex: 1 }}>
        <LayerManager
          layers={layers}
          onLayerVisibilityChange={handleLayerVisibilityChange}
          onLayerFiltersChange={handleLayerFiltersChange}
        />
      </div>
      {viewConfig && (
        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '40%' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem', padding: '1rem' }}>
            {viewConfig.config.components
              .filter(comp => comp.type === 'grid')
              .flatMap(comp => comp.visualizations)
              .map(vis => {
                const data = visualizationData[vis.id];
                if (!data) return null;

                return (
                  <div key={vis.id} style={{ background: 'white', padding: '1rem', borderRadius: '4px' }}>
                    <Plot
                      data={[
                        {
                          type: vis.type,
                          mode: vis.properties.mode,
                          x: data.x,
                          y: data.y,
                          values: data.values,
                          labels: data.labels
                        }
                      ]}
                      layout={{
                        title: vis.title,
                        ...vis.properties.layout,
                        margin: { t: 30, r: 30, l: 30, b: 30 }
                      }}
                      config={{ responsive: true }}
                      style={{ width: '100%', height: '100%' }}
                    />
                  </div>
                );
              })}
          </div>
        </div>
      )}
    </div>
  );
};

export default DynamicView; 