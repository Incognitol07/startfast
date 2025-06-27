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
            elif self.config.database_type == DatabaseType.REDIS:
                # For Redis, generate data structures/schemas instead of models
                redis_data_content = self._get_redis_data_structures_template()
                self.write_file(
                    f"{self.config.path}/app/models/data_structures.py",
                    redis_data_content,
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

    def _get_redis_data_structures_template(self) -> str:
        """Get Redis data structures template for ML API"""
        template = '''"""
Redis Data Structures for ML Predictions
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class PredictionData:
    """Data structure for ML prediction results"""
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    model_version: str
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    status: str = "completed"
    created_at: Optional[datetime] = None
    prediction_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage"""
        data = {
            "input_data": self.input_data,
            "output_data": self.output_data,
            "model_version": self.model_version,
            "confidence_score": self.confidence_score,
            "processing_time": self.processing_time,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "prediction_id": self.prediction_id
        }
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PredictionData':
        """Create from dictionary (Redis data)"""
        if "created_at" in data and data["created_at"]:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class ModelMetadata:
    """Data structure for ML model metadata"""
    name: str
    version: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage"""
        data = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "parameters": self.parameters,
            "metrics": self.metrics,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelMetadata':
        """Create from dictionary (Redis data)"""
        if "created_at" in data and data["created_at"]:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


# Redis key patterns for organizing data
class RedisKeys:
    """Redis key patterns for ML data"""
    
    @staticmethod
    def prediction(prediction_id: str) -> str:
        """Key for individual prediction"""
        return f"prediction:{prediction_id}"
    
    @staticmethod
    def predictions_by_model(model_version: str) -> str:
        """Key pattern for predictions by model version"""
        return f"predictions:model:{model_version}"
    
    @staticmethod
    def model_metadata(model_name: str) -> str:
        """Key for model metadata"""
        return f"model:metadata:{model_name}"
    
    @staticmethod
    def model_list() -> str:
        """Key for list of all models"""
        return "models:list"
    
    @staticmethod
    def prediction_stats(model_version: str) -> str:
        """Key for prediction statistics"""
        return f"stats:predictions:{model_version}"


# Utility functions for Redis operations
def serialize_for_redis(data: Any) -> str:
    """Serialize data for Redis storage"""
    if isinstance(data, (PredictionData, ModelMetadata)):
        return json.dumps(data.to_dict())
    return json.dumps(data)


def deserialize_from_redis(data: str, data_type: str) -> Any:
    """Deserialize data from Redis"""
    parsed_data = json.loads(data)
    
    if data_type == "prediction":
        return PredictionData.from_dict(parsed_data)
    elif data_type == "model_metadata":
        return ModelMetadata.from_dict(parsed_data)
    
    return parsed_data
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
