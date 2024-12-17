import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Dataset } from '../types';
import './DatasetCatalog.css';

interface DatasetCatalogProps {
  onAddDataset: (dataset: Dataset) => void;
}

export const DatasetCatalog: React.FC<DatasetCatalogProps> = ({ onAddDataset }) => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/datasets/');
      setDatasets(response.data);
    } catch (error) {
      console.error('Error fetching datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredDatasets = datasets.filter(dataset =>
    dataset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    dataset.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="dataset-catalog">
      <div className="catalog-header">
        <h3>Available Datasets</h3>
        <input
          type="text"
          placeholder="Search datasets..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>
      
      <div className="dataset-list">
        {loading ? (
          <div className="loading">Loading datasets...</div>
        ) : (
          filteredDatasets.map(dataset => (
            <div key={dataset.id} className="dataset-item">
              <div className="dataset-info">
                <h4>{dataset.name}</h4>
                <p>{dataset.description}</p>
                <div className="dataset-metadata">
                  <span>Points: {dataset.metadata.point_count}</span>
                  {dataset.metadata.categories && (
                    <span>Categories: {dataset.metadata.categories.join(', ')}</span>
                  )}
                </div>
              </div>
              <button
                onClick={() => onAddDataset(dataset)}
                className="add-button"
              >
                Add to Map
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}; 