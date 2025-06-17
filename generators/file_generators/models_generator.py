"""
Models Generator
Generates database models
"""

from ..base_generator import BaseGenerator
from ..config import ProjectType, DatabaseType


class ModelsGenerator(BaseGenerator):
    """Generates database models"""

    def generate(self):
        """Generate model files"""
        # Generate base item model for CRUD operations
        if self.config.project_type in [ProjectType.CRUD, ProjectType.API]:
            item_model_content = self._get_item_model_template()
            self.write_file(
                f"{self.config.path}/app/models/item.py", item_model_content
            )

        # Generate ML model for ML API
        if self.config.project_type == ProjectType.ML_API:
            ml_model_content = self._get_ml_model_template()
            self.write_file(
                f"{self.config.path}/app/models/prediction.py", ml_model_content
            )

    def _get_item_model_template(self) -> str:
        """Get item model template"""
        if self.config.database_type in [
            DatabaseType.SQLITE,
            DatabaseType.POSTGRESQL,
            DatabaseType.MYSQL,
        ]:
            return self._get_sqlalchemy_item_model()
        elif self.config.database_type == DatabaseType.MONGODB:
            return self._get_mongodb_item_model()
        return ""

    def _get_sqlalchemy_item_model(self) -> str:
        """Get SQLAlchemy item model"""
        template = '''"""
Item Model
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, Float
from app.db.base import BaseModel


class Item(BaseModel):
    """Item model for CRUD operations"""
    
    __tablename__ = "items"
    
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    category = Column(String(100), nullable=True, index=True)
    
    def __repr__(self):
        return f"<Item {{self.id}}: {{self.title}}>"
'''

        return self.format_template(template)

    def _get_mongodb_item_model(self) -> str:
        """Get MongoDB item model"""
        if self.config.is_async:
            template = '''"""
Item Model (MongoDB with Beanie)
"""

from typing import Optional
from beanie import Document
from pydantic import Field


class Item(Document):
    """Item model for CRUD operations"""
    
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: bool = True
    category: Optional[str] = Field(None, max_length=100)
    
    class Settings:
        name = "items"
        indexes = ["title", "category"]
'''
        else:
            template = '''"""
Item Model (MongoDB with MongoEngine)
"""

from mongoengine import Document, StringField, FloatField, BooleanField


class Item(Document):
    """Item model for CRUD operations"""
    
    title = StringField(max_length=255, required=True)
    description = StringField()
    price = FloatField()
    is_active = BooleanField(default=True)
    category = StringField(max_length=100)
    
    meta = {{
        'collection': 'items',
        'indexes': ['title', 'category']
    }}
'''

        return self.format_template(template)

    def _get_ml_model_template(self) -> str:
        """Get ML model template"""
        template = '''"""
ML Prediction Model
"""

from sqlalchemy import Column, Integer, String, Text, JSON, Float, DateTime
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

        return self.format_template(template)
