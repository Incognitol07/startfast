"""
Schemas Generator
Generates Pydantic schemas for request/response validation
"""

from ..base_generator import BaseGenerator
from ..config import ProjectType


class SchemasGenerator(BaseGenerator):
    """Generates Pydantic schemas"""

    def generate(self):
        """Generate schema files"""
        # Generate base item schemas for CRUD operations
        if self.config.project_type in [ProjectType.CRUD, ProjectType.API]:
            item_schema_content = self._get_item_schema_template()
            self.write_file(
                f"{self.config.path}/app/schemas/item.py", item_schema_content
            )

        # Generate ML schemas for ML API
        if self.config.project_type == ProjectType.ML_API:
            ml_schema_content = self._get_ml_schema_template()
            self.write_file(
                f"{self.config.path}/app/schemas/prediction.py", ml_schema_content
            )

        # Generate common schemas
        common_schema_content = self._get_common_schema_template()
        self.write_file(
            f"{self.config.path}/app/schemas/common.py", common_schema_content
        )

    def _get_item_schema_template(self) -> str:
        """Get item schema template"""
        template = '''"""
Item Schemas
Pydantic models for request/response validation
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ItemBase(BaseModel):
    """Base item schema"""
    title: str = Field(..., min_length=1, max_length=255, description="Item title")
    description: Optional[str] = Field(None, description="Item description")
    price: Optional[float] = Field(None, ge=0, description="Item price")
    category: Optional[str] = Field(None, max_length=100, description="Item category")


class ItemCreate(ItemBase):
    """Schema for creating items"""
    pass


class ItemUpdate(BaseModel):
    """Schema for updating items"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class ItemResponse(ItemBase):
    """Schema for item responses"""
    id: int
    is_active: bool
    created_at: str
    updated_at: str
    
    model_config = ConfigDict(from_attributes=True)


class ItemList(BaseModel):
    """Schema for item list responses"""
    items: list[ItemResponse]
    total: int
    page: int
    per_page: int
    pages: int
'''

        return self.format_template(template)

    def _get_ml_schema_template(self) -> str:
        """Get ML schema template"""
        template = '''"""
ML Prediction Schemas
Pydantic models for ML API request/response validation
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class PredictionInput(BaseModel):
    """Schema for prediction input"""
    features: Dict[str, Any] = Field(..., description="Input features for prediction")
    model_version: Optional[str] = Field(None, description="Specific model version to use")


class PredictionOutput(BaseModel):
    """Schema for prediction output"""
    prediction: Any = Field(..., description="Prediction result")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score")
    model_version: str = Field(..., description="Model version used")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")


class PredictionResponse(BaseModel):
    """Schema for prediction API response"""
    id: int
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    model_version: str
    confidence_score: Optional[float]
    processing_time: float
    status: str
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)


class BatchPredictionInput(BaseModel):
    """Schema for batch prediction input"""
    batch_data: List[Dict[str, Any]] = Field(..., description="Batch input data")
    model_version: Optional[str] = Field(None, description="Specific model version to use")


class BatchPredictionOutput(BaseModel):
    """Schema for batch prediction output"""
    predictions: List[PredictionOutput]
    batch_id: str
    total_processing_time: float


class ModelInfo(BaseModel):
    """Schema for model information"""
    name: str
    version: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: str
    created_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
'''

        return self.format_template(template)

    def _get_common_schema_template(self) -> str:
        """Get common schema template"""
        template = '''"""
Common Schemas
Shared Pydantic models used across the application
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(..., description="Check timestamp")


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class SuccessResponse(BaseModel):
    """Success response schema"""
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class PaginationParams(BaseModel):
    """Pagination parameters schema"""
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(10, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: Optional[str] = Field("asc", regex="^(asc|desc)$", description="Sort order")


class PaginatedResponse(BaseModel):
    """Paginated response schema"""
    items: List[Any]
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page")
    per_page: int = Field(..., ge=1, description="Items per page")
    pages: int = Field(..., ge=1, description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")


class FilterParams(BaseModel):
    """Common filter parameters"""
    search: Optional[str] = Field(None, description="Search term")
    category: Optional[str] = Field(None, description="Category filter")
    is_active: Optional[bool] = Field(None, description="Active status filter")
    created_after: Optional[str] = Field(None, description="Created after date (ISO format)")
    created_before: Optional[str] = Field(None, description="Created before date (ISO format)")
'''

        return self.format_template(template)
