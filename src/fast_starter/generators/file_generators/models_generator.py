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
            ml_model_content = self._get_ml_model_template()
            self.write_file(
                f"{self.config.path}/app/models/prediction.py", ml_model_content
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
        return f"<Prediction {{self.id}}: {{self.model_version}}>"


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
        return f"<ModelMetadata {{self.name}}: {{self.version}}>"
'''

        return template
