export interface Coordinate {
  longitude: number;
  latitude: number;
}

export interface Feature {
  id: string;
  coordinates: Coordinate;
  properties: Record<string, any>;
  timestamp?: string;
  h3_cells?: Record<number, string>;
}

export interface H3Cell {
  h3_index: string;
  resolution: number;
  center: Coordinate;
  value: number;
  properties: Record<string, any>;
}

export interface Dataset {
  id: string;
  name: string;
  description: string;
  features: Feature[];
  metadata: Record<string, any>;
  created_at: string;
  template_id?: string;
  grid_versions: Record<number, string>;
}

export interface GridDataset {
  id: string;
  name: string;
  description: string;
  resolution: number;
  cells: H3Cell[];
  metadata: Record<string, any>;
  source_dataset_id?: string;
} 