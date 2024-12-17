import { ScatterplotLayer } from '@deck.gl/layers';
import { H3HexagonLayer } from '@deck.gl/geo-layers';
import { Feature, Dataset, GridDataset } from '../types';
import axios from 'axios';

export interface Layer {
  id: string;
  visible: boolean;
  data: any;
  layer: any;
}

export class LayerService {
  static async createPointLayer(dataset: Dataset): Promise<Layer> {
    const response = await axios.get(`http://localhost:8000/datasets/${dataset.id}`);
    const data = response.data;

    return {
      id: `points-${dataset.id}`,
      visible: true,
      data,
      layer: new ScatterplotLayer({
        id: `points-${dataset.id}`,
        data: data.features,
        pickable: true,
        opacity: 0.8,
        stroked: true,
        filled: true,
        radiusScale: 6,
        radiusMinPixels: 3,
        radiusMaxPixels: 100,
        lineWidthMinPixels: 1,
        getPosition: (d: Feature) => [
          d.coordinates.longitude,
          d.coordinates.latitude
        ],
        getFillColor: (d: Feature) => {
          const value = d.properties.normalized_value || 0;
          return [
            255 * (1 - value),
            255 * value,
            0,
            255
          ];
        },
        getLineColor: () => [0, 0, 0]
      })
    };
  }

  static async createGridLayer(dataset: Dataset, resolution: number): Promise<Layer> {
    let gridData: GridDataset;
    
    try {
      // Try to get existing grid version
      const response = await axios.get(
        `http://localhost:8000/datasets/${dataset.id}/grid/${resolution}`
      );
      gridData = response.data;

      if (!gridData) {
        // Create grid version if it doesn't exist
        const createResponse = await axios.post(
          `http://localhost:8000/datasets/${dataset.id}/grid`,
          null,
          { params: { resolution } }
        );
        gridData = createResponse.data;
      }
    } catch (error) {
      // If grid version doesn't exist, create it
      const createResponse = await axios.post(
        `http://localhost:8000/datasets/${dataset.id}/grid`,
        null,
        { params: { resolution } }
      );
      gridData = createResponse.data;
    }

    return {
      id: `grid-${dataset.id}-${resolution}`,
      visible: true,
      data: gridData,
      layer: new H3HexagonLayer({
        id: `grid-${dataset.id}-${resolution}`,
        data: gridData.cells,
        pickable: true,
        extruded: true,
        elevationScale: 20,
        getHexagon: (d: any) => d.h3_index,
        getFillColor: (d: any) => {
          const value = d.value || 0;
          return [
            255 * (1 - value),
            255 * value,
            0,
            180
          ];
        },
        getElevation: (d: any) => d.value * 100
      })
    };
  }

  static updateLayerVisibility(layer: Layer, visible: boolean): Layer {
    return {
      ...layer,
      visible,
      layer: layer.layer.clone({ visible })
    };
  }

  static updateLayerStyle(layer: Layer, styleUpdates: any): Layer {
    return {
      ...layer,
      layer: layer.layer.clone(styleUpdates)
    };
  }
} 