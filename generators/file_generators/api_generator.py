"""
API Generator
Generates API endpoints and routers
"""

from ..base_generator import BaseGenerator
from ..config import ProjectType, AuthType


class APIGenerator(BaseGenerator):
    """Generates API endpoints"""

    def generate(self):
        """Generate API files"""
        # Generate main endpoints
        endpoints_content = self._get_endpoints_template()
        self.write_file(
            f"{self.config.path}/app/api/v1/endpoints.py", endpoints_content
        )

        # Generate auth endpoints if authentication is enabled
        if self.config.auth_type != AuthType.NONE:
            auth_endpoints_content = self._get_auth_endpoints_template()
            self.write_file(
                f"{self.config.path}/app/api/v1/auth.py", auth_endpoints_content
            )

    def _get_endpoints_template(self) -> str:
        """Get main endpoints template"""
        template = '''"""
Main API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
{auth_imports}
{database_imports}
{model_imports}
{schema_imports}

router = APIRouter()

{auth_endpoints_include}

@router.get("/")
async def root():
    """Root endpoint"""
    return {{"message": "Welcome to {project_name} API", "version": "1.0.0"}}


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{"status": "healthy", "service": "{project_name}"}}

{crud_endpoints}

{project_specific_endpoints}
'''

        # Customize based on configuration
        auth_imports = ""
        auth_endpoints_include = ""
        database_imports = ""
        model_imports = ""
        schema_imports = ""
        crud_endpoints = ""
        project_specific_endpoints = ""

        if self.config.auth_type != AuthType.NONE:
            auth_imports = "from app.core.security import get_current_user"
            auth_endpoints_include = """
from .auth import router as auth_router
router.include_router(auth_router, prefix="/auth", tags=["authentication"])
"""

        # Add database imports
        database_imports = "from app.db.database import get_db \nfrom app.models.auth import User"  # Add CRUD endpoints for different project types
        if self.config.project_type in [ProjectType.CRUD, ProjectType.API]:
            crud_endpoints = self._get_crud_endpoints()
            model_imports = "from app.models.item import Item"
            schema_imports = (
                "from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse"
            )

        # Add project-specific endpoints
        if self.config.project_type == ProjectType.ML_API:
            project_specific_endpoints = self._get_ml_endpoints()
        elif self.config.project_type == ProjectType.MICROSERVICE:
            project_specific_endpoints = self._get_microservice_endpoints()

        return template.format(
            project_name=self.get_template_vars()["project_name"],
            auth_imports=auth_imports,
            auth_endpoints_include=auth_endpoints_include,
            database_imports=database_imports,
            model_imports=model_imports,
            schema_imports=schema_imports,
            crud_endpoints=crud_endpoints,
            project_specific_endpoints=project_specific_endpoints,
        )

    def _get_crud_endpoints(self) -> str:
        """Get CRUD endpoints template"""
        if self.config.is_async:
            return '''
@router.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = {{Depends(get_current_user) if {auth_imports} else None}}
):
    """Create a new item"""
    from app.services.item_service import create_item
    return await create_item(db, item)


@router.get("/items/", response_model=list[ItemResponse])
async def read_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = {{Depends(get_current_user) if {auth_imports} else None}}
):
    """Get all items"""
    from app.services.item_service import get_items    return await get_items(db, skip=skip, limit=limit)


@router.get("/items/{{item_id}}", response_model=ItemResponse)
async def read_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = {{Depends(get_current_user) if {auth_imports} else None}}
):
    """Get item by ID"""
    from app.services.item_service import get_item
    item = await get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")    return item


@router.put("/items/{{item_id}}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = {{Depends(get_current_user) if {auth_imports} else None}}
):
    """Update item by ID"""
    from app.services.item_service import update_item
    updated_item = await update_item(db, item_id, item)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item


@router.delete("/items/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = {{Depends(get_current_user) if {auth_imports} else None}}
):
    """Delete item by ID"""
    from app.services.item_service import delete_item
    success = await delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
'''
        else:
            return '''
@router.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = {{Depends(get_current_user) if {auth_imports} else None}}
):
    """Create a new item"""
    from app.services.item_service import create_item
    return create_item(db, item)


@router.get("/items/", response_model=list[ItemResponse])
def read_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = {{Depends(get_current_user) if {auth_imports} else None}}
):
    """Get all items"""
    from app.services.item_service import get_items    return get_items(db, skip=skip, limit=limit)


@router.get("/items/{{item_id}}", response_model=ItemResponse)
def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = {{Depends(get_current_user) if {auth_imports} else None}}
):
    """Get item by ID"""
    from app.services.item_service import get_item
    item = get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/items/{{item_id}}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = {{Depends(get_current_user) if {auth_imports} else None}}
):
    """Update item by ID"""
    from app.services.item_service import update_item
    updated_item = update_item(db, item_id, item)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item


@router.delete("/items/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = {{Depends(get_current_user) if {auth_imports} else None}}
):
    """Delete item by ID"""
    from app.services.item_service import delete_item
    success = delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
'''

    def _get_ml_endpoints(self) -> str:
        """Get ML API specific endpoints"""
        return '''
@router.post("/predict")
async def predict(
    input_data: dict,
    current_user: User = {{Depends(get_current_user) if {auth_imports} else None}}
):
    """Make ML prediction"""
    from app.services.prediction_service import make_prediction    try:
        result = await make_prediction(input_data)
        return {"prediction": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/model/info")
async def get_model_info(
    current_user: User = {{Depends(get_current_user) if {auth_imports} else None}}
):    """Get ML model information"""
    return {
        "model_name": "DefaultModel",
        "version": "1.0.0",
        "description": "Machine Learning model for predictions"
    }
'''

    def _get_microservice_endpoints(self) -> str:
        """Get microservice specific endpoints"""
        return '''
@router.get("/status")
async def service_status():
    """Get service status"""
    return {
        "service": "{project_name}",
        "status": "running",
        "version": "1.0.0"
    }


@router.post("/process")
async def process_data(
    data: dict,
    current_user: User = {{Depends(get_current_user) if {auth_imports} else None}}
):
    """Process data"""
    from app.services.processing_service import process_data
    try:
        result = await process_data(data)
        return {"result": result, "status": "processed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
'''

    def _get_auth_endpoints_template(self) -> str:
        """Get authentication endpoints template"""
        template = '''"""
Authentication Endpoints
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
{auth_security_imports}
from app.core.config import settings
from app.db.database import get_db
from app.schemas.auth import Token, UserLogin, UserCreate, User as UserSchema
from app.core.security import authenticate_user, create_access_token, get_current_user, create_user

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login endpoint to get access token"""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={{"WWW-Authenticate": "Bearer"}},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={{"sub": user.email}}, expires_delta=access_token_expires
    )
    
    return {{"access_token": access_token, "token_type": "bearer"}}


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register new user"""
    # Check if user already exists
    from app.core.security import get_user_by_email
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = await create_user(db, user_data.email, user_data.password)
    return user


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: UserSchema = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_user_me(
    user_update: dict,
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):    
    """Update current user information"""
    # Implementation for updating user profile
    # This is a placeholder - implement based on your needs
    return current_user
'''

        auth_security_imports = "from sqlalchemy.orm import Session"

        return template.format(auth_security_imports=auth_security_imports)
