from fastapi import APIRouter, HTTPException
from app.core.config import settings
import boto3
import pandas as pd
from typing import Dict, Any, List
from io import BytesIO

router = APIRouter()

@router.post("/")
async def get_filtered_data(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Retrieve and process aircraft and antenna data based on filters
    """
    try:
        s3 = boto3.client('s3', region_name=settings.AWS_REGION)
        
        # Read aircraft positions
        aircraft_response = s3.get_object(
            Bucket=settings.DATA_BUCKET,
            Key='aircraft/positions.parquet'
        )
        aircraft_data = pd.read_parquet(BytesIO(aircraft_response['Body'].read()))
        
        # Read antenna data
        antenna_response = s3.get_object(
            Bucket=settings.DATA_BUCKET,
            Key='antennas/metadata.csv'
        )
        antenna_data = pd.read_csv(BytesIO(antenna_response['Body'].read()))
        
        # Apply filters
        if 'date_range' in filters:
            start_date, end_date = filters['date_range'].split('_')
            aircraft_data = aircraft_data[
                (aircraft_data['timestamp'] >= start_date) &
                (aircraft_data['timestamp'] <= end_date)
            ]
            
        if 'frequency_bands' in filters:
            antenna_data = antenna_data[
                antenna_data['frequency_bands'].apply(
                    lambda x: any(band in x for band in filters['frequency_bands'])
                )
            ]
        
        # Merge data
        merged_data = pd.merge(
            aircraft_data,
            antenna_data,
            left_on='linked_antenna',
            right_on='antenna_id',
            how='inner'
        )
        
        return merged_data.to_dict(orient='records')
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing data: {str(e)}"
        ) 