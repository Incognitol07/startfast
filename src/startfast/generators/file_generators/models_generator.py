"""
Models Generator
Generates database models
"""

from ...generators.base_generator import BaseGenerator
from ...core.config import ProjectType, DatabaseType


class ModelsGenerator(BaseGenerator):
    """Generates database models"""

    def generate(self):
        """Generate model files"""
        # Generate ML model for ML API
        if self.config.project_type == ProjectType.ML_API:
            # Only generate SQL-based models for SQL databases
            if self.should_generate_sqlalchemy_files():
                ml_model_content = self._get_ml_model_template()
                self.write_file(
                    f"{self.config.path}/app/models/prediction.py", ml_model_content
                )
            elif self.config.database_type == DatabaseType.MONGODB:
                # For MongoDB, generate Beanie models
                mongodb_model_content = self._get_mongodb_model_template()
                self.write_file(
                    f"{self.config.path}/app/models/prediction.py",
                    mongodb_model_content,
                )

    def _get_ml_model_template(self) -> str:
        """Get ML model template"""
        template = '''"""
ML Prediction Model
"""

from sqlalchemy import Column, Integer, String, Text, JSON, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import BaseModel


class Prediction(BaseModel):
    """Model for storing ML predictions"""
    
    __tablename__ = "predictions"
    
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=False)
    model_version = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)  # in seconds
    status = Column(String(20), default="completed")
    
    def __repr__(self):
        return f"<Prediction {self.id}: {self.model_version}>"


class ModelMetadata(BaseModel):
    """Model for storing ML model metadata"""
    
    __tablename__ = "model_metadata"
    
    name = Column(String(100), nullable=False, unique=True)
    version = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<ModelMetadata {self.name}: {self.version}>"
'''

        return template

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
