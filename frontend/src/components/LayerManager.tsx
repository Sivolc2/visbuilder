import React, { useState, useEffect } from 'react';
import { Card, Switch, Collapse, Space, Typography, Button } from 'antd';
import { DataService, ColumnMetadata, FilterDefinition } from '../services/dataService';
import DataFilter from './DataFilter';

const { Panel } = Collapse;
const { Text } = Typography;

interface Layer {
  id: string;
  name: string;
  type: string;
  data_source: string;
  visible: boolean;
}

interface LayerManagerProps {
  layers: Layer[];
  onLayerVisibilityChange: (layerId: string, visible: boolean) => void;
  onLayerFiltersChange: (layerId: string, filters: FilterDefinition[]) => void;
}

const LayerManager: React.FC<LayerManagerProps> = ({
  layers,
  onLayerVisibilityChange,
  onLayerFiltersChange,
}) => {
  const [columnMetadata, setColumnMetadata] = useState<Record<string, ColumnMetadata[]>>({});
  const dataService = DataService.getInstance();

  const resetAllFilters = () => {
    layers.forEach(layer => {
      onLayerFiltersChange(layer.id, []);
    });
  };

  useEffect(() => {
    const fetchColumnMetadata = async () => {
      const uniqueDataSources = [...new Set(layers.map(layer => layer.data_source))];
      const metadata: Record<string, ColumnMetadata[]> = {};
      
      for (const sourceId of uniqueDataSources) {
        try {
          metadata[sourceId] = await dataService.getColumnMetadata(sourceId);
        } catch (error) {
          console.error(`Error fetching column metadata for ${sourceId}:`, error);
        }
      }
      
      setColumnMetadata(metadata);
    };

    fetchColumnMetadata();
  }, [layers]);

  const getCollapseItems = () => {
    return layers.map(layer => ({
      key: layer.id,
      label: (
        <Space>
          <Switch
            checked={layer.visible}
            onChange={(checked) => onLayerVisibilityChange(layer.id, checked)}
          />
          <Text>{layer.name}</Text>
        </Space>
      ),
      children: (
        <div>
          <div style={{ padding: '8px 0' }}>
            <Text strong>Type: </Text>
            <Text>{layer.type}</Text>
          </div>
          <div style={{ padding: '8px 0' }}>
            <Text strong>Data Source: </Text>
            <Text>{layer.data_source}</Text>
          </div>
          {columnMetadata[layer.data_source] && (
            <div style={{ padding: '8px 0' }}>
              <Text strong>Filters</Text>
              <DataFilter
                columns={columnMetadata[layer.data_source]}
                onFiltersChange={(filters) => onLayerFiltersChange(layer.id, filters)}
              />
            </div>
          )}
        </div>
      )
    }));
  };

  return (
    <Card title="Layer Manager" style={{ width: 400, maxHeight: '80vh', overflowY: 'auto' }}>
      <Button 
        onClick={resetAllFilters}
        style={{ marginBottom: '1rem', width: '100%' }}
        type="primary"
      >
        Reset All Filters
      </Button>
      <Collapse items={getCollapseItems()} />
    </Card>
  );
};

export default LayerManager; 