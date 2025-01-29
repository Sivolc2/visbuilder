import React, { useEffect, useState } from 'react';
import { Select, Input, Button, Space, Form, InputNumber } from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';
import { ColumnMetadata, FilterDefinition } from '../services/dataService';

const { Option } = Select;

interface DataFilterProps {
  columns: ColumnMetadata[];
  onFiltersChange: (filters: FilterDefinition[]) => void;
}

const DataFilter: React.FC<DataFilterProps> = ({ columns, onFiltersChange }) => {
  const [form] = Form.useForm();

  const getOperatorOptions = (columnType: string) => {
    if (columnType === 'categorical') {
      return [
        { label: 'Equals', value: 'equals' },
        { label: 'Contains', value: 'contains' },
        { label: 'In List', value: 'in' }
      ];
    }
    return [
      { label: 'Equals', value: 'equals' },
      { label: 'Greater Than', value: 'greater_than' },
      { label: 'Less Than', value: 'less_than' }
    ];
  };

  const renderValueInput = (columnName: string, fieldName: number) => {
    const column = columns.find(col => col.name === columnName);
    if (!column) return null;

    if (column.type === 'categorical' && column.unique_values) {
      return (
        <Select mode="multiple" style={{ width: '100%' }}>
          {column.unique_values.map(value => (
            <Option key={value} value={value}>{value}</Option>
          ))}
        </Select>
      );
    }

    if (column.type === 'numerical') {
      return (
        <InputNumber
          style={{ width: '100%' }}
          min={column.min}
          max={column.max}
        />
      );
    }

    return <Input />;
  };

  const handleValuesChange = () => {
    const values = form.getFieldsValue();
    const filters = values.filters?.filter((f: any) => 
      f && f.column && f.operator && f.value
    ) || [];
    onFiltersChange(filters);
  };

  return (
    <Form
      form={form}
      onValuesChange={handleValuesChange}
      initialValues={{ filters: [{}] }}
    >
      <Form.List name="filters">
        {(fields, { add, remove }) => (
          <>
            {fields.map(({ key, name, ...restField }) => (
              <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                <Form.Item
                  {...restField}
                  name={[name, 'column']}
                  rules={[{ required: true, message: 'Missing column' }]}
                >
                  <Select
                    style={{ width: 200 }}
                    placeholder="Select column"
                    onChange={() => form.setFieldValue(['filters', name, 'value'], undefined)}
                  >
                    {columns.map(col => (
                      <Option key={col.name} value={col.name}>{col.name}</Option>
                    ))}
                  </Select>
                </Form.Item>
                <Form.Item
                  {...restField}
                  name={[name, 'operator']}
                  rules={[{ required: true, message: 'Missing operator' }]}
                >
                  <Select style={{ width: 150 }} placeholder="Select operator">
                    {getOperatorOptions(
                      columns.find(col => col.name === form.getFieldValue(['filters', name, 'column']))?.type || 'categorical'
                    ).map(op => (
                      <Option key={op.value} value={op.value}>{op.label}</Option>
                    ))}
                  </Select>
                </Form.Item>
                <Form.Item
                  {...restField}
                  name={[name, 'value']}
                  rules={[{ required: true, message: 'Missing value' }]}
                >
                  {renderValueInput(form.getFieldValue(['filters', name, 'column']), name)}
                </Form.Item>
                <MinusCircleOutlined onClick={() => remove(name)} />
              </Space>
            ))}
            <Form.Item>
              <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                Add Filter
              </Button>
            </Form.Item>
          </>
        )}
      </Form.List>
    </Form>
  );
};

export default DataFilter; 