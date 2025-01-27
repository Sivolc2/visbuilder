from fastapi import APIRouter, HTTPException
from app.core.config import settings
import boto3
import yaml
from typing import Dict, Any

router = APIRouter()

@router.get("/")
async def get_dashboard_config() -> Dict[str, Any]:
    """
    Retrieve and process the YAML configuration from S3
    """
    try:
        s3 = boto3.client('s3', region_name=settings.AWS_REGION)
        response = s3.get_object(
            Bucket=settings.CONFIG_BUCKET,
            Key='dashboard_config.yaml'
        )
        yaml_content = response['Body'].read().decode('utf-8')
        config = yaml.safe_load(yaml_content)
        
        # Basic validation
        required_keys = ['dashboard', 'data_sources', 'visualizations']
        if not all(key in config for key in required_keys):
            raise HTTPException(
                status_code=400,
                detail="Invalid configuration: missing required sections"
            )
            
        return config
        
    except s3.exceptions.NoSuchKey:
        raise HTTPException(
            status_code=404,
            detail="Configuration file not found"
        )
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid YAML format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing configuration: {str(e)}"
        ) 