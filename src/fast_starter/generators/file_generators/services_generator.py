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

        # Generate Redis service when Redis is selected as database
        if self.config.database_type == DatabaseType.REDIS:
            redis_service_content = self._get_redis_service_template()
            self.write_file(
                f"{self.config.path}/app/services/redis_service.py",
                redis_service_content,
            )

    def _get_ml_service_template(self) -> str:
        """Get ML service template"""
        return '''"""
ML Prediction Service
Business logic for ML predictions
"""

import logging
from typing import Dict, Any, List
import joblib
import numpy as np
from app.core.config import settings

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for ML predictions"""
    
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the ML model"""
        try:
            # Placeholder - replace with your actual model loading logic
            logger.info("Loading ML model...")
            # self.model = joblib.load("path/to/your/model.pkl")
            logger.info("ML model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            self.model = None
    
    async def make_prediction(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction using the loaded model"""
        if not self.model:
            raise ValueError("Model not loaded")
        
        try:
            # Placeholder prediction logic
            # Replace with your actual prediction code
            features = self._preprocess_input(input_data)
            prediction = self._predict(features)
            confidence = self._calculate_confidence(features)
            
            return {
                "prediction": prediction,
                "confidence": confidence,
                "model_version": "1.0.0"
            }
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise ValueError(f"Prediction error: {str(e)}")
    
    def _preprocess_input(self, input_data: Dict[str, Any]) -> np.ndarray:
        """Preprocess input data"""
        # Placeholder preprocessing - implement your logic
        # return processed_features
        return np.array([1, 2, 3])  # Placeholder
    
    def _predict(self, features: np.ndarray) -> Any:
        """Make prediction with the model"""
        # Placeholder prediction - implement your logic
        # return self.model.predict(features)
        return "sample_prediction"  # Placeholder
    
    def _calculate_confidence(self, features: np.ndarray) -> float:
        """Calculate prediction confidence"""
        # Placeholder confidence calculation - implement your logic
        return 0.95  # Placeholder


# Service instance
prediction_service = PredictionService()


async def make_prediction(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Make ML prediction"""
    return await prediction_service.make_prediction(input_data)


def get_model_info() -> Dict[str, Any]:
    """Get model information"""
    return {
        "name": "DefaultModel",
        "version": "1.0.0",
        "description": "Machine Learning model for predictions",
        "status": "loaded" if prediction_service.model else "not_loaded"
    }
'''

    def _get_processing_service_template(self) -> str:
        """Get processing service template"""
        return '''"""
Processing Service
Business logic for data processing
"""

import logging
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class ProcessingService:
    """Service for data processing"""
    
    def __init__(self):
        self.processors = self._initialize_processors()
    
    def _initialize_processors(self) -> Dict[str, Any]:
        """Initialize processing components"""
        return {
            "validator": self._create_validator(),
            "transformer": self._create_transformer(),
            "analyzer": self._create_analyzer()
        }
    
    def _create_validator(self):
        """Create data validator"""
        # Implement your data validation logic
        return lambda data: True  # Placeholder
    
    def _create_transformer(self):
        """Create data transformer"""
        # Implement your data transformation logic
        return lambda data: data  # Placeholder
    
    def _create_analyzer(self):
        """Create data analyzer"""
        # Implement your data analysis logic
        return lambda data: {"status": "analyzed"}  # Placeholder
    
    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data"""
        try:
            # Step 1: Validate data
            if not self.processors["validator"](data):
                raise ValueError("Data validation failed")
            
            # Step 2: Transform data
            transformed_data = self.processors["transformer"](data)
            
            # Step 3: Analyze data
            analysis_result = self.processors["analyzer"](transformed_data)
            
            return {
                "processed_data": transformed_data,
                "analysis": analysis_result,
                "status": "success",
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            raise ValueError(f"Processing error: {str(e)}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


# Service instance
processing_service = ProcessingService()


async def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process data using the processing service"""
    return await processing_service.process_data(data)


def get_service_status() -> Dict[str, Any]:
    """Get processing service status"""
    return {
        "service": "ProcessingService",
        "status": "running",
        "processors": list(processing_service.processors.keys()),
        "version": "1.0.0"
    }
'''

    def _get_redis_service_template(self) -> str:
        """Get Redis service template"""
        return '''"""
Redis Service
Generic Redis service for key-value operations and caching
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """Generic Redis service for key-value operations"""
    
    def __init__(self):
        self.redis_client = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8"
            )
            logger.info("Redis connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {e}")
            self.redis_client = None
    
    async def ping(self) -> bool:
        """Test Redis connection"""
        try:
            if not self.redis_client:
                return False
            result = await self.redis_client.ping()
            return result
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    async def set(
        self, 
        key: str, 
        value: Union[str, Dict, List], 
        expire: Optional[int] = None
    ) -> bool:
        """Set a value in Redis"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            # Serialize complex data types
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            result = await self.redis_client.set(key, value, ex=expire)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False
    
    async def get(self, key: str, deserialize: bool = True) -> Optional[Any]:
        """Get a value from Redis"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            value = await self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to deserialize JSON data
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            
            return value
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None
    
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys from Redis"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            result = await self.redis_client.delete(*keys)
            return int(result)
        except Exception as e:
            logger.error(f"Failed to delete keys {keys}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            result = await self.redis_client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to check existence of key {key}: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for a key"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            result = await self.redis_client.expire(key, seconds)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to set expiration for key {key}: {e}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """Get time to live for a key"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            result = await self.redis_client.ttl(key)
            return int(result)
        except Exception as e:
            logger.error(f"Failed to get TTL for key {key}: {e}")
            return -1
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in Redis"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            result = await self.redis_client.incrby(key, amount)
            return int(result)
        except Exception as e:
            logger.error(f"Failed to increment key {key}: {e}")
            return 0
    
    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement a numeric value in Redis"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            result = await self.redis_client.decrby(key, amount)
            return int(result)
        except Exception as e:
            logger.error(f"Failed to decrement key {key}: {e}")
            return 0
    
    async def get_keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching a pattern"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            keys = await self.redis_client.keys(pattern)
            return keys
        except Exception as e:
            logger.error(f"Failed to get keys with pattern {pattern}: {e}")
            return []
    
    async def flush_db(self) -> bool:
        """Flush current database (use with caution!)"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            result = await self.redis_client.flushdb()
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to flush database: {e}")
            return False
    
    # Hash operations
    async def hset(self, key: str, field: str, value: Union[str, Dict, List]) -> bool:
        """Set field in a hash"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            result = await self.redis_client.hset(key, field, value)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to set hash field {field} in key {key}: {e}")
            return False
    
    async def hget(self, key: str, field: str, deserialize: bool = True) -> Optional[Any]:
        """Get field from a hash"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            value = await self.redis_client.hget(key, field)
            if value is None:
                return None
            
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            
            return value
        except Exception as e:
            logger.error(f"Failed to get hash field {field} from key {key}: {e}")
            return None
    
    async def hgetall(self, key: str, deserialize: bool = True) -> Dict[str, Any]:
        """Get all fields from a hash"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            result = await self.redis_client.hgetall(key)
            if not result:
                return {}
            
            if deserialize:
                deserialized = {}
                for field, value in result.items():
                    try:
                        deserialized[field] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        deserialized[field] = value
                return deserialized
            
            return result
        except Exception as e:
            logger.error(f"Failed to get all fields from hash key {key}: {e}")
            return {}
    
    async def hdel(self, key: str, *fields: str) -> int:
        """Delete fields from a hash"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            result = await self.redis_client.hdel(key, *fields)
            return int(result)
        except Exception as e:
            logger.error(f"Failed to delete hash fields {fields} from key {key}: {e}")
            return 0
    
    # List operations
    async def lpush(self, key: str, *values: Union[str, Dict, List]) -> int:
        """Push values to the left of a list"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value))
                else:
                    serialized_values.append(value)
            
            result = await self.redis_client.lpush(key, *serialized_values)
            return int(result)
        except Exception as e:
            logger.error(f"Failed to push to list key {key}: {e}")
            return 0
    
    async def rpush(self, key: str, *values: Union[str, Dict, List]) -> int:
        """Push values to the right of a list"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value))
                else:
                    serialized_values.append(value)
            
            result = await self.redis_client.rpush(key, *serialized_values)
            return int(result)
        except Exception as e:
            logger.error(f"Failed to push to list key {key}: {e}")
            return 0
    
    async def lpop(self, key: str, deserialize: bool = True) -> Optional[Any]:
        """Pop value from the left of a list"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            value = await self.redis_client.lpop(key)
            if value is None:
                return None
            
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            
            return value
        except Exception as e:
            logger.error(f"Failed to pop from list key {key}: {e}")
            return None
    
    async def rpop(self, key: str, deserialize: bool = True) -> Optional[Any]:
        """Pop value from the right of a list"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            value = await self.redis_client.rpop(key)
            if value is None:
                return None
            
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            
            return value
        except Exception as e:
            logger.error(f"Failed to pop from list key {key}: {e}")
            return None
    
    async def lrange(self, key: str, start: int = 0, end: int = -1, deserialize: bool = True) -> List[Any]:
        """Get range of values from a list"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            values = await self.redis_client.lrange(key, start, end)
            if not values:
                return []
            
            if deserialize:
                deserialized = []
                for value in values:
                    try:
                        deserialized.append(json.loads(value))
                    except (json.JSONDecodeError, TypeError):
                        deserialized.append(value)
                return deserialized
            
            return values
        except Exception as e:
            logger.error(f"Failed to get range from list key {key}: {e}")
            return []
    
    async def llen(self, key: str) -> int:
        """Get length of a list"""
        try:
            if not self.redis_client:
                raise RuntimeError("Redis client not initialized")
            
            result = await self.redis_client.llen(key)
            return int(result)
        except Exception as e:
            logger.error(f"Failed to get length of list key {key}: {e}")
            return 0
    
    async def close(self):
        """Close Redis connection"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")


# Service instance
redis_service = RedisService()


# Convenience functions for common operations
async def cache_set(key: str, value: Any, expire: Optional[int] = None) -> bool:
    """Cache a value with optional expiration"""
    return await redis_service.set(f"cache:{key}", value, expire)


async def cache_get(key: str) -> Optional[Any]:
    """Get a cached value"""
    return await redis_service.get(f"cache:{key}")


async def cache_delete(key: str) -> bool:
    """Delete a cached value"""
    result = await redis_service.delete(f"cache:{key}")
    return result > 0


async def session_set(session_id: str, data: Dict[str, Any], expire: int = 3600) -> bool:
    """Store session data"""
    return await redis_service.set(f"session:{session_id}", data, expire)


async def session_get(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session data"""
    return await redis_service.get(f"session:{session_id}")


async def session_delete(session_id: str) -> bool:
    """Delete session data"""
    result = await redis_service.delete(f"session:{session_id}")
    return result > 0


async def rate_limit_check(key: str, limit: int, window: int) -> Dict[str, Any]:
    """Simple rate limiting check"""
    current_count = await redis_service.increment(f"rate_limit:{key}")
    
    if current_count == 1:
        # First request in window, set expiration
        await redis_service.expire(f"rate_limit:{key}", window)
    
    remaining = max(0, limit - current_count)
    is_allowed = current_count <= limit
    
    return {
        "allowed": is_allowed,
        "count": current_count,
        "remaining": remaining,
        "reset_time": window
    }


# TODO: Add your custom Redis operations here

def get_redis_info() -> Dict[str, Any]:
    """Get Redis service information"""
    return {
        "service": "RedisService",
        "status": "running" if redis_service.redis_client else "disconnected",
        "version": "1.0.0",
        "description": "Generic Redis service for key-value operations and caching"
    }
'''
