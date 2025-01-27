import axios from 'axios';

export type DataSource = 'S3' | 'API' | 'LOCAL';

export interface DataFetchConfig {
  source: DataSource;
  url: string;
  bucket?: string;
  key?: string;
  region?: string;
  params?: Record<string, any>;
}

export interface ColumnMetadata {
  name: string;
  type: 'categorical' | 'numerical';
  unique_values?: any[];
  min?: number;
  max?: number;
}

export interface FilterDefinition {
  column: string;
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than' | 'in';
  value: any;
}

export class DataService {
  private static instance: DataService;
  private baseUrl: string;

  private constructor() {
    this.baseUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:5003';
  }

  public static getInstance(): DataService {
    if (!DataService.instance) {
      DataService.instance = new DataService();
    }
    return DataService.instance;
  }

  /**
   * Fetch data from various sources (S3, API, or local)
   */
  async fetchData<T>(config: DataFetchConfig): Promise<T> {
    try {
      switch (config.source) {
        case 'S3':
          return await this.fetchFromS3<T>(config);
        case 'API':
          return await this.fetchFromAPI<T>(config);
        case 'LOCAL':
          return await this.fetchLocal<T>(config);
        default:
          throw new Error('Unsupported data source');
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      throw error;
    }
  }

  /**
   * Fetch data from S3 through backend proxy
   */
  private async fetchFromS3<T>(config: DataFetchConfig): Promise<T> {
    if (!config.bucket || !config.key) {
      throw new Error('Bucket and key are required for S3 data source');
    }

    const response = await axios.get(`${this.baseUrl}/api/data/s3`, {
      params: {
        bucket: config.bucket,
        key: config.key,
        region: config.region || 'us-east-1',
        ...config.params
      }
    });

    return response.data;
  }

  /**
   * Fetch data from a REST API
   */
  private async fetchFromAPI<T>(config: DataFetchConfig): Promise<T> {
    const response = await axios.get(config.url, {
      params: config.params
    });

    return response.data;
  }

  /**
   * Fetch data from local backend
   */
  private async fetchLocal<T>(config: DataFetchConfig): Promise<T> {
    const response = await axios.get(`${this.baseUrl}${config.url}`, {
      params: config.params
    });

    return response.data;
  }

  async getColumnMetadata(sourceId: string): Promise<ColumnMetadata[]> {
    try {
      const response = await axios.get(`${this.baseUrl}/api/data/${sourceId}/columns`);
      return response.data;
    } catch (error) {
      console.error('Error fetching column metadata:', error);
      throw error;
    }
  }

  async getFilteredData<T>(sourceId: string, filters: FilterDefinition[]): Promise<T[]> {
    try {
      const response = await axios.post(`${this.baseUrl}/api/data/${sourceId}/filtered`, { filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching filtered data:', error);
      throw error;
    }
  }

  /**
   * Cache management methods could be added here
   */
}

// Example usage:
/*
const dataService = DataService.getInstance();

// Fetch from S3
const s3Data = await dataService.fetchData({
  source: 'S3',
  bucket: 'my-bucket',
  key: 'data/points.geojson',
  region: 'us-west-2'
});

// Fetch from API
const apiData = await dataService.fetchData({
  source: 'API',
  url: 'https://api.example.com/data'
});

// Fetch from local backend
const localData = await dataService.fetchData({
  source: 'LOCAL',
  url: '/api/data/local'
});
*/ 