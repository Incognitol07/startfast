"""
Services Generator
Generates business logic services
"""

from ..base_generator import BaseGenerator
from ..config import ProjectType, DatabaseType


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


async def get_items_count(
    db: AsyncSession,
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None
) -> int:
    """Get total count of items with filters"""
    query = select(func.count(Item.id))
    
    # Apply filters
    if search:
        query = query.filter(Item.title.contains(search))
    if category:
        query = query.filter(Item.category == category)
    if is_active is not None:
        query = query.filter(Item.is_active == is_active)
    
    result = await db.execute(query)
    return result.scalar()
'''
        else:
            template = '''"""
Item Service (SQLAlchemy)
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


def get_items_count(
    db: Session,
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None
) -> int:
    """Get total count of items with filters"""
    query = db.query(Item)
    
    # Apply filters
    if search:
        query = query.filter(Item.title.contains(search))
    if category:
        query = query.filter(Item.category == category)
    if is_active is not None:
        query = query.filter(Item.is_active == is_active)
    
    return query.count()
'''

        return self.format_template(template)

    def _get_mongodb_item_service(self) -> str:
        """Get MongoDB item service"""
        if self.config.is_async:
            template = '''"""
Item Service (MongoDB with Beanie)
Business logic for item operations
"""

from typing import List, Optional
from beanie import PydanticObjectId
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


async def create_item(item_data: ItemCreate) -> Item:
    """Create a new item"""
    item = Item(**item_data.model_dump())
    await item.insert()
    return item


async def get_item(item_id: str) -> Optional[Item]:
    """Get item by ID"""
    return await Item.get(PydanticObjectId(item_id))


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
        query = query.find({{Item.title: {{"$regex": search, "$options": "i"}}}})
    if category:
        query = query.find({{Item.category: category}})
    if is_active is not None:
        query = query.find({{Item.is_active: is_active}})
    
    # Apply pagination
    return await query.skip(skip).limit(limit).to_list()


async def update_item(item_id: str, item_data: ItemUpdate) -> Optional[Item]:
    """Update item by ID"""
    item = await Item.get(PydanticObjectId(item_id))
    
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
    item = await Item.get(PydanticObjectId(item_id))
    
    if not item:
        return False
    
    await item.delete()
    return True


async def get_items_count(
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None
) -> int:
    """Get total count of items with filters"""
    query = Item.find()
    
    # Apply filters
    if search:
        query = query.find({{Item.title: {{"$regex": search, "$options": "i"}}}})
    if category:
        query = query.find({{Item.category: category}})
    if is_active is not None:
        query = query.find({{Item.is_active: is_active}})
    
    return await query.count()
'''
        else:
            template = '''"""
Item Service (MongoDB with MongoEngine)
Business logic for item operations
"""

from typing import List, Optional
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def create_item(item_data: ItemCreate) -> Item:
    """Create a new item"""
    item = Item(**item_data.model_dump())
    item.save()
    return item


def get_item(item_id: str) -> Optional[Item]:
    """Get item by ID"""
    try:
        return Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        return None


def get_items(
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[Item]:
    """Get items with pagination and filters"""
    query = Item.objects
    
    # Apply filters
    if search:
        query = query.filter(title__icontains=search)
    if category:
        query = query.filter(category=category)
    if is_active is not None:
        query = query.filter(is_active=is_active)
    
    # Apply pagination
    return list(query.skip(skip).limit(limit))


def update_item(item_id: str, item_data: ItemUpdate) -> Optional[Item]:
    """Update item by ID"""
    try:
        item = Item.objects.get(id=item_id)
        
        # Update fields
        update_data = item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        item.save()
        return item
    except Item.DoesNotExist:
        return None


def delete_item(item_id: str) -> bool:
    """Delete item by ID"""
    try:
        item = Item.objects.get(id=item_id)
        item.delete()
        return True
    except Item.DoesNotExist:
        return False


def get_items_count(
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None
) -> int:
    """Get total count of items with filters"""
    query = Item.objects
    
    # Apply filters
    if search:
        query = query.filter(title__icontains=search)
    if category:
        query = query.filter(category=category)
    if is_active is not None:
        query = query.filter(is_active=is_active)
    
    return query.count()
'''

        return self.format_template(template)

    def _get_ml_service_template(self) -> str:
        """Get ML service template"""
        template = '''"""
ML Prediction Service
Business logic for machine learning predictions
"""

import time
import asyncio
from typing import Any, Dict, List
import numpy as np
from app.schemas.prediction import PredictionInput, PredictionOutput


class MLModel:
    """Placeholder ML model class"""
    
    def __init__(self, model_name: str = "DefaultModel", version: str = "1.0.0"):
        self.model_name = model_name
        self.version = version
        self.is_loaded = False
    
    def load(self):
        """Load the ML model"""
        # Placeholder for model loading logic
        # In a real implementation, you would load your trained model here
        # Example: self.model = joblib.load('model.pkl')
        self.is_loaded = True
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction using the model"""
        if not self.is_loaded:
            self.load()
        
        # Placeholder prediction logic
        # In a real implementation, you would use your actual model
        # Example: prediction = self.model.predict([list(features.values())])
        
        # Mock prediction for demonstration
        prediction_value = sum(v for v in features.values() if isinstance(v, (int, float))) * 0.1
        confidence = min(0.95, max(0.5, abs(prediction_value) / 10))
        
        return {{
            "value": prediction_value,
            "confidence": confidence,
            "category": "positive" if prediction_value > 0 else "negative"
        }}


# Global model instance
_model_instance = None


def get_model() -> MLModel:
    """Get or create model instance"""
    global _model_instance
    if _model_instance is None:
        _model_instance = MLModel()
        _model_instance.load()
    return _model_instance


async def make_prediction(input_data: Dict[str, Any]) -> PredictionOutput:
    """Make ML prediction"""
    start_time = time.time()
    
    try:
        # Get model instance
        model = get_model()
        
        # Make prediction
        if asyncio.iscoroutinefunction(model.predict):
            prediction_result = await model.predict(input_data)
        else:
            # Run CPU-intensive prediction in thread pool
            loop = asyncio.get_event_loop()
            prediction_result = await loop.run_in_executor(
                None, model.predict, input_data
            )
        
        processing_time = time.time() - start_time
        
        return PredictionOutput(
            prediction=prediction_result,
            confidence=prediction_result.get("confidence"),
            model_version=model.version,
            processing_time=processing_time
        )
    
    except Exception as e:
        processing_time = time.time() - start_time
        raise Exception(f"Prediction failed: {{str(e)}}") from e


async def batch_predict(batch_data: List[Dict[str, Any]]) -> List[PredictionOutput]:
    """Make batch predictions"""
    results = []
    
    # Process predictions concurrently
    tasks = [make_prediction(data) for data in batch_data]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and return successful predictions
    successful_results = []
    for result in results:
        if isinstance(result, PredictionOutput):
            successful_results.append(result)
        else:
            # Log error in production
            print(f"Prediction error: {{result}}")
    
    return successful_results


def get_model_info() -> Dict[str, Any]:
    """Get model information"""
    model = get_model()
    return {{
        "name": model.model_name,
        "version": model.version,
        "status": "loaded" if model.is_loaded else "not_loaded",
        "description": "Machine learning model for predictions"
    }}
'''

        return self.format_template(template)

    def _get_processing_service_template(self) -> str:
        """Get processing service template"""
        template = '''"""
Processing Service
Business logic for data processing in microservices
"""

import asyncio
import time
from typing import Any, Dict, List, Optional


class DataProcessor:
    """Data processing service"""
    
    def __init__(self):
        self.processing_stats = {{
            "total_processed": 0,
            "success_count": 0,
            "error_count": 0
        }}
    
    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data"""
        start_time = time.time()
        
        try:
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            # Example processing logic
            processed_data = {{
                "input": data,
                "processed_at": time.time(),
                "processing_time": time.time() - start_time,
                "result": self._apply_processing_logic(data)
            }}
            
            self.processing_stats["total_processed"] += 1
            self.processing_stats["success_count"] += 1
            
            return processed_data
            
        except Exception as e:
            self.processing_stats["total_processed"] += 1
            self.processing_stats["error_count"] += 1
            raise Exception(f"Processing failed: {{str(e)}}") from e
    
    def _apply_processing_logic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply actual processing logic"""
        # Placeholder processing logic
        # Replace with your actual business logic
        
        result = {{}}
        
        # Example: transform numeric values
        for key, value in data.items():
            if isinstance(value, (int, float)):
                result[f"processed_{{key}}"] = value * 2
            elif isinstance(value, str):
                result[f"processed_{{key}}"] = value.upper()
            else:
                result[f"processed_{{key}}"] = value
        
        # Add processing metadata
        result["processing_metadata"] = {{
            "total_fields": len(data),
            "numeric_fields": sum(1 for v in data.values() if isinstance(v, (int, float))),
            "string_fields": sum(1 for v in data.values() if isinstance(v, str))
        }}
        
        return result
    
    async def batch_process(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple data items"""
        tasks = [self.process_data(data) for data in batch_data]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_results = []
        for result in results:
            if isinstance(result, dict):
                successful_results.append(result)
            else:
                # Log error in production
                print(f"Processing error: {{result}}")
        
        return successful_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {{
            **self.processing_stats,
            "success_rate": (
                self.processing_stats["success_count"] / 
                max(1, self.processing_stats["total_processed"])
            ) * 100
        }}


# Global processor instance
_processor_instance = None


def get_processor() -> DataProcessor:
    """Get or create processor instance"""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = DataProcessor()
    return _processor_instance


async def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process data using the global processor"""
    processor = get_processor()
    return await processor.process_data(data)


async def batch_process_data(batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Batch process data using the global processor"""
    processor = get_processor()
    return await processor.batch_process(batch_data)


def get_processing_stats() -> Dict[str, Any]:
    """Get processing statistics"""
    processor = get_processor()
    return processor.get_stats()
'''

        return self.format_template(template)
