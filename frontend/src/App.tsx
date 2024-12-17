import React, { useState, useCallback } from 'react';
import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl';
import { ViewState } from '@deck.gl/core';
import { DatasetCatalog } from './components/DatasetCatalog';
import { LayerService, Layer } from './services/LayerService';
import { Dataset } from './types';
import './App.css';

const INITIAL_VIEW_STATE: ViewState = {
  longitude: -122.41669,
  latitude: 37.7853,
  zoom: 13,
  pitch: 0,
  bearing: 0
};

function App() {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
  const [layers, setLayers] = useState<Layer[]>([]);

  const handleAddDataset = useCallback(async (dataset: Dataset) => {
    try {
      // Create point layer
      const pointLayer = await LayerService.createPointLayer(dataset);
      
      // Create grid layer (resolution 9 for city-level detail)
      const gridLayer = await LayerService.createGridLayer(dataset, 9);
      
      setLayers(prevLayers => [...prevLayers, pointLayer, gridLayer]);
    } catch (error) {
      console.error('Error adding dataset:', error);
    }
  }, []);

  const visibleLayers = layers
    .filter(layer => layer.visible)
    .map(layer => layer.layer);

  return (
    <div className="map-container">
      <DatasetCatalog onAddDataset={handleAddDataset} />
      
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={visibleLayers}
        onViewStateChange={({ viewState }) => setViewState(viewState)}
      >
        <Map
          mapStyle="mapbox://styles/mapbox/dark-v9"
          mapboxAccessToken={process.env.REACT_APP_MAPBOX_TOKEN}
        />
      </DeckGL>
    </div>
  );
}

export default App; 