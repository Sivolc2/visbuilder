import React, { useEffect, useState, useCallback, useRef, useMemo } from 'react';
import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl';
import Plot from 'react-plotly.js';
import { ViewState } from '@deck.gl/core';
import { LineLayer, PolygonLayer, ScatterplotLayer } from '@deck.gl/layers';
import { HeatmapLayer } from '@deck.gl/aggregation-layers';
import { H3HexagonLayer } from '@deck.gl/geo-layers';
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

interface H3Feature {
  hex: string;
  value: number;
  point_count: number;
}

interface H3Collection {
  type: 'H3Collection';
  features: H3Feature[];
}

interface LayerConfig {
  id: string;
  name: string;
  type: string;
  data_source: string;
  properties: Record<string, any>;
}

interface GeoJSONFeature {
  type: 'Feature';
  geometry: {
    type: string;
    coordinates: number[];
  };
  properties: Record<string, any>;
}

interface ViewStateChangeParams {
  viewState: ViewState;
}

const DynamicView: React.FC<DynamicViewProps> = ({ viewId, mapboxToken }) => {
  const [viewConfig, setViewConfig] = useState<ViewConfig | null>(null);
  const [viewState, setViewState] = useState<ViewState>({
    longitude: -122.4194,  // Default center, will be updated from config
    latitude: 37.7749,
    zoom: 12,
    pitch: 0,
    bearing: 0
  });
  const [layerData, setLayerData] = useState<Record<string, any>>({});
  const [visualizationData, setVisualizationData] = useState<Record<string, any>>({});
  const [layers, setLayers] = useState<LayerState[]>([]);
  const [error, setError] = useState<string | null>(null);
  const mapRef = useRef<any>(null);

  const fetchViewConfig = async () => {
    try {
      const response = await axios.get<ViewConfig>(`${config.API_BASE_URL}/views/${viewId}`);
      setViewConfig(response.data);
      
      // Update view state based on configuration
      if (response.data?.config?.settings) {
        const { center, default_zoom } = response.data.config.settings;
        setViewState(prev => ({
          ...prev,
          longitude: center[0],
          latitude: center[1],
          zoom: default_zoom || prev.zoom
        }));
      }
    } catch (error) {
      setError('Error loading view configuration');
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
      console.log(`Fetching data for layer: ${layer.id} with config:`, {
        type: layer.type,
        properties: layer.properties
      });
      
      const response = await axios.post(
        `${config.API_BASE_URL}/data/${layer.data_source}/filtered`,
        { 
          filters: layer.filters,
          layer_config: {
            type: layer.type,
            properties: layer.properties
          }
        }
      );
      
      console.log(`Received data for layer ${layer.id}:`, {
        type: response.data.type,
        featureCount: response.data.features?.length,
        firstFeature: response.data.features?.[0]
      });
      
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
        .flatMap(comp => comp.layers.map((layer: LayerConfig) => ({
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

  const deckLayers = useMemo(() => {
    if (!viewConfig) return [];

    console.log('Recomputing deck layers');
    return layers
      .filter(layer => layer.visible && layerData[layer.id])
      .map(layer => {
        const data = layerData[layer.id];
        console.log(`Creating deck.gl layer for ${layer.id}:`, { 
          type: layer.type, 
          features: data.features?.length,
          firstFeature: data.features?.[0],
          layerConfig: layer.properties
        });
        
        switch (layer.type) {
          case 'scatterplot': {
            console.log('Creating scatterplot layer');
            return new ScatterplotLayer({
              id: layer.id,
              data: data.features,
              getPosition: (d: GeoJSONFeature) => d.geometry.coordinates,
              getFillColor: layer.properties.getFillColor || [255, 140, 0],
              getRadius: layer.properties.getRadius || 5000,
              radiusScale: 1,
              radiusMinPixels: 5,
              radiusMaxPixels: 15,
              opacity: layer.properties.opacity || 0.8,
              pickable: true,
              updateTriggers: {
                getFillColor: [layer.properties.getFillColor],
                getRadius: [layer.properties.getRadius]
              },
              onHover: (info: any) => {
                if (info.object) {
                  const { properties } = info.object;
                  info.object = properties;
                }
              }
            });
          }
          
          case 'heatmap': {
            console.log('Creating heatmap layer');
            return new HeatmapLayer({
              id: layer.id,
              data: data.features,
              getPosition: (d: GeoJSONFeature) => d.geometry.coordinates,
              getWeight: (d: GeoJSONFeature) => d.properties.intensity || 1,
              colorRange: layer.properties.colorRange,
              intensity: layer.properties.intensity || 1,
              threshold: layer.properties.threshold || 0.1,
              radiusPixels: layer.properties.radiusPixels || 60,
              opacity: layer.properties.opacity || 0.6,
              updateTriggers: {
                getWeight: [layer.properties.intensity]
              }
            });
          }
          
          case 'polygon': {
            // For polygon layers, we expect preprocessed H3 data
            console.log('Creating H3 hexagon layer with data:', {
              type: data.type,
              featureCount: data.features?.length,
              firstFeature: data.features?.[0],
              layerConfig: layer.properties
            });

            const h3Data = data as H3Collection;
            if (!h3Data.features || !Array.isArray(h3Data.features)) {
              console.error('Invalid H3 data format:', h3Data);
              return null;
            }

            return new H3HexagonLayer({
              id: layer.id,
              data: h3Data.features,
              pickable: true,
              stroked: true,
              filled: true,
              extruded: false,
              wireframe: true,
              getHexagon: (d: H3Feature) => d.hex,
              getFillColor: (d: H3Feature) => {
                if (typeof d.value !== 'number') return [0, 0, 0, 0];
                const colorRange = layer.properties.getFillColor?.colorRange || 
                  [[255, 255, 178], [254, 204, 92], [253, 141, 60], [240, 59, 32], [189, 0, 38]];
                const values = h3Data.features.map(f => f.value).filter((v): v is number => typeof v === 'number');
                const maxValue = Math.max(...values);
                const index = Math.floor((d.value / maxValue) * (colorRange.length - 1));
                return colorRange[Math.min(index, colorRange.length - 1)];
              },
              getLineColor: [255, 255, 255],
              lineWidthMinPixels: 1,
              opacity: layer.properties.opacity || 0.6,
              coverage: 1,
              updateTriggers: {
                getFillColor: [layer.properties.getFillColor]
              },
              onHover: (info: any) => {
                if (info.object) {
                  info.object = {
                    value: info.object.value,
                    point_count: info.object.point_count
                  };
                }
              }
            });
          }
          
          default: {
            console.warn(`Unknown layer type: ${layer.type}`);
            return null;
          }
        }
      })
      .filter(Boolean);
  }, [viewConfig, layers, layerData]);

  const fetchVisualizationData = async () => {
    if (!viewConfig) return;

    try {
      const visualizations = viewConfig.config.components
        .filter(comp => comp.type === 'grid')
        .flatMap(comp => comp.visualizations);

      for (const vis of visualizations) {
        try {
          const response = await axios.get(`${config.API_BASE_URL}/data/${vis.data_source}`);
          const sourceData = response.data;
          const records = sourceData.data || []; // Use data field from response

          if (vis.type === 'line') {
            setVisualizationData(prev => ({
              ...prev,
              [vis.id]: {
                x: records.map((d: any) => d.Epoch),
                y: records.map((d: any) => d.Flight_Usage_Mbps),
                type: 'scatter',
                mode: 'lines+markers'
              }
            }));
          } else if (vis.type === 'pie') {
            // Group by airline and sum up usage
            const airlineData = records.reduce((acc: any, curr: any) => {
              const airline = curr.Airline;
              const usage = curr.Flight_Usage_Mbps;
              acc[airline] = (acc[airline] || 0) + usage;
              return acc;
            }, {});
            
            setVisualizationData(prev => ({
              ...prev,
              [vis.id]: {
                values: Object.values(airlineData),
                labels: Object.keys(airlineData),
                type: 'pie'
              }
            }));
          } else if (vis.type === 'bar') {
            // Group by Terminal_Type and calculate average usage
            const terminalData = records.reduce((acc: any, curr: any) => {
              const type = curr.Terminal_Type;
              const usage = curr.Flight_Usage_Mbps;
              if (!acc[type]) {
                acc[type] = { total: 0, count: 0 };
              }
              acc[type].total += usage;
              acc[type].count += 1;
              return acc;
            }, {});
            
            const averages = Object.entries(terminalData).map(([type, data]: [string, any]) => ({
              type,
              average: data.total / data.count
            }));
            
            setVisualizationData(prev => ({
              ...prev,
              [vis.id]: {
                x: averages.map(d => d.type),
                y: averages.map(d => d.average),
                type: 'bar'
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
        (viewConfig.config.settings?.refresh_rate || 30) * 1000  // Default to 30 seconds if not specified
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
        onViewStateChange={({ viewState }: ViewStateChangeParams) => setViewState(viewState)}
        controller={true}
        layers={deckLayers}
      >
        {mapboxToken && (
          <Map
            ref={mapRef}
            mapboxAccessToken={mapboxToken}
            mapStyle="mapbox://styles/mapbox/dark-v10"
            reuseMaps
          />
        )}
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

                const layout = {
                  title: {
                    text: vis.title,
                    font: {
                      size: 16,
                      color: '#333'
                    }
                  },
                  showlegend: true,
                  margin: { t: 40, r: 30, l: 40, b: 40 },
                  height: 250,
                  paper_bgcolor: 'white',
                  plot_bgcolor: 'white',
                  ...vis.properties.layout
                };

                return (
                  <div key={vis.id} style={{ 
                    background: 'white', 
                    padding: '1rem', 
                    borderRadius: '4px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }}>
                    <Plot
                      data={[
                        {
                          type: vis.type,
                          mode: vis.properties.mode,
                          x: data.x,
                          y: data.y,
                          values: data.values,
                          labels: data.labels,
                          hoverinfo: 'all',
                          textinfo: 'value'
                        }
                      ]}
                      layout={layout}
                      config={{ 
                        responsive: true,
                        displayModeBar: false // Hide the plotly toolbar
                      }}
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