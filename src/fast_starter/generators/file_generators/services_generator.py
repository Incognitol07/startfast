"""
Services Generator
Generates business logic services
"""

from ...generators.base_generator import BaseGenerator
from ...core.config import ProjectType, DatabaseType


class ServicesGenerator(BaseGenerator):
    """Generates service layer files"""

    def generate(self):
        """Generate service files"""
        # Generate base item service for CRUD operations
        if self.config.project_type in [ProjectType.CRUD, ProjectType.API]:
            item_service_content = self._get_item_service_template()
            self.write_file(
                f"{self.config.path}/app/services/item_service.py", item_service_content
            )

        # Generate ML service for ML API
        if self.config.project_type == ProjectType.ML_API:
            ml_service_content = self._get_ml_service_template()
            self.write_file(
                f"{self.config.path}/app/services/prediction_service.py",
                ml_service_content,
            )

        # Generate processing service for microservices
        if self.config.project_type == ProjectType.MICROSERVICE:
            processing_service_content = self._get_processing_service_template()
            self.write_file(
                f"{self.config.path}/app/services/processing_service.py",
                processing_service_content,
            )

    def _get_item_service_template(self) -> str:
        """Get item service template"""
        if self.config.database_type in [
            DatabaseType.SQLITE,
            DatabaseType.POSTGRESQL,
            DatabaseType.MYSQL,
        ]:
            return self._get_sqlalchemy_item_service()
        elif self.config.database_type == DatabaseType.MONGODB:
            return self._get_mongodb_item_service()
        return ""

    def _get_sqlalchemy_item_service(self) -> str:
        """Get SQLAlchemy item service"""
        if self.config.is_async:
            template = '''"""
Item Service (Async SQLAlchemy)
Business logic for item operations
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


async def create_item(db: AsyncSession, item_data: ItemCreate) -> Item:
    """Create a new item"""
    item = Item(**item_data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def get_item(db: AsyncSession, item_id: int) -> Optional[Item]:
    """Get item by ID"""
    result = await db.execute(select(Item).filter(Item.id == item_id))
    return result.scalars().first()


async def get_items(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[Item]:
    """Get items with pagination and filters"""
    query = select(Item)
    
    # Apply filters
    if search:
        query = query.filter(Item.title.contains(search))
    if category:
        query = query.filter(Item.category == category)
    if is_active is not None:
        query = query.filter(Item.is_active == is_active)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def update_item(db: AsyncSession, item_id: int, item_data: ItemUpdate) -> Optional[Item]:
    """Update item by ID"""
    result = await db.execute(select(Item).filter(Item.id == item_id))
    item = result.scalars().first()
    
    if not item:
        return None
    
    # Update fields
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, item_id: int) -> bool:
    """Delete item by ID"""
    result = await db.execute(select(Item).filter(Item.id == item_id))
    item = result.scalars().first()
    
    if not item:
        return False
    
    await db.delete(item)
    await db.commit()
    return True
'''
        else:
            template = '''"""
Item Service (Sync SQLAlchemy)
Business logic for item operations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def create_item(db: Session, item_data: ItemCreate) -> Item:
    """Create a new item"""
    item = Item(**item_data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_item(db: Session, item_id: int) -> Optional[Item]:
    """Get item by ID"""
    return db.query(Item).filter(Item.id == item_id).first()


def get_items(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[Item]:
    """Get items with pagination and filters"""
    query = db.query(Item)
    
    # Apply filters
    if search:
        query = query.filter(Item.title.contains(search))
    if category:
        query = query.filter(Item.category == category)
    if is_active is not None:
        query = query.filter(Item.is_active == is_active)
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()


def update_item(db: Session, item_id: int, item_data: ItemUpdate) -> Optional[Item]:
    """Update item by ID"""
    item = db.query(Item).filter(Item.id == item_id).first()
    
    if not item:
        return None
    
    # Update fields
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item_id: int) -> bool:
    """Delete item by ID"""
    item = db.query(Item).filter(Item.id == item_id).first()
    
    if not item:
        return False
    
    db.delete(item)
    db.commit()
    return True
'''

        return template

    def _get_mongodb_item_service(self) -> str:
        """Get MongoDB item service"""
        return '''"""
Item Service (MongoDB)
Business logic for item operations
"""

from typing import List, Optional
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


async def create_item(item_data: ItemCreate) -> Item:
    """Create a new item"""
    item = Item(**item_data.model_dump())
    await item.insert()
    return item


async def get_item(item_id: str) -> Optional[Item]:
    """Get item by ID"""
    return await Item.get(item_id)


async def get_items(
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[Item]:
    """Get items with pagination and filters"""
    query = Item.find()
    
    # Apply filters
    if search:
        query = query.find({{Item.title: {{"$regex": search, "$options": "i"}}}}})
    if category:
        query = query.find({{Item.category: category}})
    if is_active is not None:
        query = query.find({{Item.is_active: is_active}})
    
    # Apply pagination
    return await query.skip(skip).limit(limit).to_list()


async def update_item(item_id: str, item_data: ItemUpdate) -> Optional[Item]:
    """Update item by ID"""
    item = await Item.get(item_id)
    
    if not item:
        return None
    
    # Update fields
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await item.save()
    return item


async def delete_item(item_id: str) -> bool:
    """Delete item by ID"""
    item = await Item.get(item_id)
    
    if not item:
        return False
    
    await item.delete()
    return True
'''

    def _get_ml_service_template(self) -> str:
        """Get ML service template"""
        return '''"""
ML Prediction Service
Business logic for ML predictions
"""

import asyncio
import time
from typing import Dict, Any
from app.models.prediction import Prediction


async def make_prediction(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Make ML prediction"""
    start_time = time.time()
    
    # Placeholder for actual ML model inference
    # Replace this with your actual ML model
    prediction_result = {{
        "prediction": "sample_result",
        "probability": 0.85
    }}
    
    processing_time = time.time() - start_time
    
    # Store prediction in database
    prediction = Prediction(
        input_data=input_data,
        output_data=prediction_result,
        model_version="1.0.0",
        confidence_score=prediction_result.get("probability"),
        processing_time=processing_time
    )
    
    # Save prediction (implement based on your database choice)
    # await prediction.save()
    
    return prediction_result


async def get_model_info() -> Dict[str, Any]:
    """Get model information"""
    return {{
        "name": "DefaultModel",
        "version": "1.0.0",
        "description": "Default ML model for predictions",
        "status": "active"
    }}
'''

    def _get_processing_service_template(self) -> str:
        """Get processing service template"""
        return '''"""
Processing Service
Business logic for data processing
"""

import asyncio
from typing import Dict, Any


async def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process incoming data"""
    # Placeholder for actual data processing
    # Implement your business logic here
    
    processed_data = {{
        "original": data,
        "processed": True,
        "timestamp": "2024-01-01T00:00:00Z",
        "status": "completed"
    }}
    
    return processed_data


async def validate_data(data: Dict[str, Any]) -> bool:
    """Validate incoming data"""
    # Implement data validation logic
    required_fields = ["id", "type"]
    
    for field in required_fields:
        if field not in data:
            return False
    
    return True
'''
