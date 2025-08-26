"""
Models Generator
Generates database models
"""

from ...generators.base_generator import BaseGenerator
from ...core.config import ProjectType, DatabaseType


class ModelsGenerator(BaseGenerator):
    """Generates database models"""

    def _get_mongodb_model_template(self) -> str:
        """Get MongoDB model template for ML API"""
        template = '''"""
MongoDB Models for ML Predictions
"""

from typing import Dict, Any, Optional
from datetime import datetime
from beanie import Document
from pydantic import Field


class Prediction(Document):
    """MongoDB model for storing ML predictions"""
    
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    model_version: str
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None  # in seconds
    status: str = "completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "predictions"
        indexes = [
            "model_version",
            "status",
            "created_at",
        ]
    
    def __repr__(self):
        return f"<Prediction {self.id}: {self.model_version}>"


class ModelMetadata(Document):
    """MongoDB model for storing ML model metadata"""
    
    name: str = Field(..., unique=True)
    version: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "model_metadata"
        indexes = [
            "name",
            "version",
            "is_active",
        ]
    
    def __repr__(self):
        return f"<ModelMetadata {self.name}: {self.version}>"
'''
