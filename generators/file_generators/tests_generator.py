"""
Tests Generator
Generates test files and configuration
"""

from ..base_generator import BaseGenerator
from ..config import ProjectType, AuthType


class TestsGenerator(BaseGenerator):
    """Generates test files"""

    def should_generate(self) -> bool:
        """Only generate if tests are enabled"""
        return self.config.include_tests

    def generate(self):
        """Generate test files"""
        # Generate test configuration
        conftest_content = self._get_conftest_template()
        self.write_file(f"{self.config.path}/tests/conftest.py", conftest_content)

        # Generate API tests
        api_test_content = self._get_api_test_template()
        self.write_file(
            f"{self.config.path}/tests/api/test_endpoints.py", api_test_content
        )

        # Generate service tests if CRUD
        if self.config.project_type in [ProjectType.CRUD, ProjectType.API]:
            service_test_content = self._get_service_test_template()
            self.write_file(
                f"{self.config.path}/tests/services/test_item_service.py",
                service_test_content,
            )

        # Generate auth tests if authentication is enabled
        if self.config.auth_type != AuthType.NONE:
            auth_test_content = self._get_auth_test_template()
            self.write_file(
                f"{self.config.path}/tests/api/test_auth.py", auth_test_content
            )

        # Generate pytest configuration
        pytest_ini_content = self._get_pytest_ini_template()
        self.write_file(f"{self.config.path}/pytest.ini", pytest_ini_content)

    def _get_conftest_template(self) -> str:
        """Get pytest configuration template"""
        template = '''"""
Test Configuration
Pytest fixtures and configuration
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import get_db, Base
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={{"check_same_thread": False}},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client"""
    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client"""
    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as async_test_client:
        yield async_test_client
    
    # Clean up
    app.dependency_overrides.clear()


{auth_fixtures}

@pytest.fixture(scope="function")
def sample_item_data():
    """Sample item data for testing"""
    return {
        "title": "Test Item",
        "description": "A test item description",        "price": 29.99,
        "category": "test"
    }


@pytest.fixture(scope="function")
def sample_items_data():
    """Sample items data for testing"""
    return [
        {
            "title": "Item 1",
            "description": "First test item",
            "price": 10.99,
            "category": "category1"
        },
        {            "title": "Item 2", 
            "description": "Second test item",
            "price": 20.99,
            "category": "category2"
        },
        {
            "title": "Item 3",
            "description": "Third test item", 
            "price": 30.99,
            "category": "category1"
        }
    ]
'''  # Add auth fixtures if authentication is enabled
        auth_fixtures = ""
        if self.config.auth_type != AuthType.NONE:
            auth_fixtures = '''

@pytest.fixture(scope="function")
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture(scope="function")
def auth_headers(client, sample_user_data):
    """Get authentication headers for testing"""
    # Register user
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201
    
    # Login to get token
    login_data = {
        "email": sample_user_data["email"],
        "password": sample_user_data["password"]
    }
    response = client.post("/api/v1/auth/token", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
'''

        return template.replace("{auth_fixtures}", auth_fixtures)

    def _get_api_test_template(self) -> str:
        """Get API test template"""
        template = '''"""
API Endpoint Tests
"""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "{project_name}" in data["message"]


def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "{project_name}"


def test_app_health_check(client: TestClient):
    """Test application health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


{crud_tests}

{project_specific_tests}


@pytest.mark.asyncio
async def test_async_endpoints(async_client):
    """Test async endpoints"""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
'''

        # Add CRUD tests if applicable
        crud_tests = ""
        if self.config.project_type in [ProjectType.CRUD, ProjectType.API]:
            crud_tests = self._get_crud_tests()  # Add project-specific tests
        project_specific_tests = ""
        if self.config.project_type == ProjectType.ML_API:
            project_specific_tests = self._get_ml_tests()

        return template.format(
            project_name=self.config.name,
            crud_tests=crud_tests,
            project_specific_tests=project_specific_tests,
        )

    def _get_crud_tests(self) -> str:
        """Get CRUD endpoint tests"""
        auth_param = ", auth_headers" if self.config.auth_type != AuthType.NONE else ""

        return f'''
def test_create_item(client: TestClient, sample_item_data{auth_param}):
    """Test creating an item"""
    headers = auth_headers if auth_headers else {{}}
    response = client.post("/api/v1/items/", json=sample_item_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_item_data["title"]
    assert data["description"] == sample_item_data["description"]
    assert data["price"] == sample_item_data["price"]
    assert "id" in data


def test_get_items(client: TestClient{auth_param}):
    """Test getting items list"""
    headers = auth_headers if auth_headers else {{}}
    response = client.get("/api/v1/items/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_item_by_id(client: TestClient, sample_item_data{auth_param}):
    """Test getting item by ID"""
    headers = auth_headers if auth_headers else {{}}
    
    # Create an item first
    create_response = client.post("/api/v1/items/", json=sample_item_data, headers=headers)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    # Get the item
    response = client.get(f"/api/v1/items/{{item_id}}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["title"] == sample_item_data["title"]


def test_update_item(client: TestClient, sample_item_data{auth_param}):
    """Test updating an item"""
    headers = auth_headers if auth_headers else {{}}
    
    # Create an item first
    create_response = client.post("/api/v1/items/", json=sample_item_data, headers=headers)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    # Update the item
    update_data = {{"title": "Updated Title", "price": 39.99}}
    response = client.put(f"/api/v1/items/{{item_id}}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["price"] == 39.99


def test_delete_item(client: TestClient, sample_item_data{auth_param}):
    """Test deleting an item"""
    headers = auth_headers if auth_headers else {{}}
    
    # Create an item first
    create_response = client.post("/api/v1/items/", json=sample_item_data, headers=headers)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    # Delete the item
    response = client.delete(f"/api/v1/items/{{item_id}}", headers=headers)
    assert response.status_code == 204
    
    # Verify item is deleted
    get_response = client.get(f"/api/v1/items/{{item_id}}", headers=headers)
    assert get_response.status_code == 404


def test_get_nonexistent_item(client: TestClient{auth_param}):
    """Test getting non-existent item"""
    headers = auth_headers if auth_headers else {{}}
    response = client.get("/api/v1/items/999", headers=headers)
    assert response.status_code == 404
'''

    def _get_ml_tests(self) -> str:
        """Get ML API specific tests"""
        auth_param = ", auth_headers" if self.config.auth_type != AuthType.NONE else ""

        return f'''
def test_prediction_endpoint(client: TestClient{auth_param}):
    """Test ML prediction endpoint"""
    headers = auth_headers if auth_headers else {{}}
    
    prediction_data = {{
        "feature1": 1.0,
        "feature2": 2.0,
        "feature3": 3.0
    }}
    
    response = client.post("/api/v1/predict", json=prediction_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "status" in data
    assert data["status"] == "success"


def test_model_info_endpoint(client: TestClient{auth_param}):
    """Test model info endpoint"""
    headers = auth_headers if auth_headers else {{}}  
    response = client.get("/api/v1/model/info", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "version" in data
    assert "description" in data


def test_invalid_prediction_data(client: TestClient{auth_param}):
    """Test prediction with invalid data"""
    headers = auth_headers if auth_headers else {{}}
    
    invalid_data = {{"invalid": "data"}}
    
    response = client.post("/api/v1/predict", json=invalid_data, headers=headers)
    # Should handle gracefully, either 400 or 422
    assert response.status_code in [400, 422]
'''

    def _get_service_test_template(self) -> str:
        """Get service test template"""
        if self.config.is_async:
            template = '''"""
Item Service Tests
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.item_service import (
    create_item, get_item, get_items, update_item, delete_item
)
from app.schemas.item import ItemCreate, ItemUpdate


@pytest.mark.asyncio
async def test_create_item_service(db_session: AsyncSession, sample_item_data):
    """Test creating item via service"""
    item_create = ItemCreate(**sample_item_data)
    item = await create_item(db_session, item_create)
    
    assert item.title == sample_item_data["title"]
    assert item.description == sample_item_data["description"]
    assert item.price == sample_item_data["price"]
    assert item.id is not None


@pytest.mark.asyncio
async def test_get_item_service(db_session: AsyncSession, sample_item_data):
    """Test getting item via service"""
    # Create item first
    item_create = ItemCreate(**sample_item_data)
    created_item = await create_item(db_session, item_create)
    
    # Get item
    retrieved_item = await get_item(db_session, created_item.id)
    
    assert retrieved_item is not None
    assert retrieved_item.id == created_item.id
    assert retrieved_item.title == sample_item_data["title"]


@pytest.mark.asyncio
async def test_get_items_service(db_session: AsyncSession, sample_items_data):
    """Test getting items list via service"""
    # Create multiple items
    for item_data in sample_items_data:
        item_create = ItemCreate(**item_data)
        await create_item(db_session, item_create)
    
    # Get items
    items = await get_items(db_session, skip=0, limit=10)
    
    assert len(items) == len(sample_items_data)


@pytest.mark.asyncio
async def test_update_item_service(db_session: AsyncSession, sample_item_data):
    """Test updating item via service"""
    # Create item first
    item_create = ItemCreate(**sample_item_data)
    created_item = await create_item(db_session, item_create)
    
    # Update item
    update_data = ItemUpdate(title="Updated Title", price=99.99)
    updated_item = await update_item(db_session, created_item.id, update_data)
    
    assert updated_item is not None
    assert updated_item.title == "Updated Title"
    assert updated_item.price == 99.99
    assert updated_item.description == sample_item_data["description"]  # Unchanged


@pytest.mark.asyncio
async def test_delete_item_service(db_session: AsyncSession, sample_item_data):
    """Test deleting item via service"""
    # Create item first
    item_create = ItemCreate(**sample_item_data)
    created_item = await create_item(db_session, item_create)
    
    # Delete item
    success = await delete_item(db_session, created_item.id)
    assert success is True
    
    # Verify item is deleted
    deleted_item = await get_item(db_session, created_item.id)
    assert deleted_item is None


@pytest.mark.asyncio
async def test_get_nonexistent_item_service(db_session: AsyncSession):
    """Test getting non-existent item via service"""
    item = await get_item(db_session, 999)
    assert item is None


@pytest.mark.asyncio
async def test_delete_nonexistent_item_service(db_session: AsyncSession):
    """Test deleting non-existent item via service"""
    success = await delete_item(db_session, 999)
    assert success is False
'''
        else:
            template = '''"""
Item Service Tests
"""

import pytest
from sqlalchemy.orm import Session
from app.services.item_service import (
    create_item, get_item, get_items, update_item, delete_item
)
from app.schemas.item import ItemCreate, ItemUpdate


def test_create_item_service(db_session: Session, sample_item_data):
    """Test creating item via service"""
    item_create = ItemCreate(**sample_item_data)
    item = create_item(db_session, item_create)
    
    assert item.title == sample_item_data["title"]
    assert item.description == sample_item_data["description"]
    assert item.price == sample_item_data["price"]
    assert item.id is not None


def test_get_item_service(db_session: Session, sample_item_data):
    """Test getting item via service"""
    # Create item first
    item_create = ItemCreate(**sample_item_data)
    created_item = create_item(db_session, item_create)
    
    # Get item
    retrieved_item = get_item(db_session, created_item.id)
    
    assert retrieved_item is not None
    assert retrieved_item.id == created_item.id
    assert retrieved_item.title == sample_item_data["title"]


def test_get_items_service(db_session: Session, sample_items_data):
    """Test getting items list via service"""
    # Create multiple items
    for item_data in sample_items_data:
        item_create = ItemCreate(**item_data)
        create_item(db_session, item_create)
    
    # Get items
    items = get_items(db_session, skip=0, limit=10)
    
    assert len(items) == len(sample_items_data)


def test_update_item_service(db_session: Session, sample_item_data):
    """Test updating item via service"""
    # Create item first
    item_create = ItemCreate(**sample_item_data)
    created_item = create_item(db_session, item_create)
    
    # Update item
    update_data = ItemUpdate(title="Updated Title", price=99.99)
    updated_item = update_item(db_session, created_item.id, update_data)
    
    assert updated_item is not None
    assert updated_item.title == "Updated Title"
    assert updated_item.price == 99.99
    assert updated_item.description == sample_item_data["description"]  # Unchanged


def test_delete_item_service(db_session: Session, sample_item_data):
    """Test deleting item via service"""
    # Create item first
    item_create = ItemCreate(**sample_item_data)
    created_item = create_item(db_session, item_create)
    
    # Delete item
    success = delete_item(db_session, created_item.id)
    assert success is True
    
    # Verify item is deleted
    deleted_item = get_item(db_session, created_item.id)
    assert deleted_item is None


def test_get_nonexistent_item_service(db_session: Session):
    """Test getting non-existent item via service"""
    item = get_item(db_session, 999)
    assert item is None


def test_delete_nonexistent_item_service(db_session: Session):
    """Test deleting non-existent item via service"""
    success = delete_item(db_session, 999)
    assert success is False
'''

        return self.format_template(template)

    def _get_auth_test_template(self) -> str:
        """Get authentication test template"""
        template = '''"""
Authentication Tests
"""

import pytest
from fastapi.testclient import TestClient


def test_register_user(client: TestClient, sample_user_data):
    """Test user registration"""
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == sample_user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data  # Should not return password


def test_register_duplicate_user(client: TestClient, sample_user_data):
    """Test registering duplicate user"""
    # Register user first time
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201
    
    # Try to register same user again
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_user(client: TestClient, sample_user_data):
    """Test user login"""
    # Register user first
    client.post("/api/v1/auth/register", json=sample_user_data)
    
    # Login
    login_data = {{
        "email": sample_user_data["email"],
        "password": sample_user_data["password"]
    }}
    response = client.post("/api/v1/auth/token", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_user(client: TestClient):
    """Test login with invalid credentials"""
    login_data = {{
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }}
    response = client.post("/api/v1/auth/token", json=login_data)
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_get_current_user(client: TestClient, auth_headers):
    """Test getting current user info"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "id" in data


def test_get_current_user_without_token(client: TestClient):
    """Test getting current user without authentication"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token(client: TestClient):
    """Test getting current user with invalid token"""
    headers = {{"Authorization": "Bearer invalid-token"}}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


def test_register_invalid_email(client: TestClient, sample_user_data):
    """Test registration with invalid email"""
    invalid_data = sample_user_data.copy()
    invalid_data["email"] = "invalid-email"
    
    response = client.post("/api/v1/auth/register", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_register_weak_password(client: TestClient, sample_user_data):
    """Test registration with weak password"""
    weak_data = sample_user_data.copy()
    weak_data["password"] = "123"
    
    response = client.post("/api/v1/auth/register", json=weak_data)
    # Depending on validation, might be 400 or 422
    assert response.status_code in [400, 422]
'''

        return self.format_template(template)

    def _get_pytest_ini_template(self) -> str:
        """Get pytest.ini template"""
        return """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    auth: marks tests that require authentication
asyncio_mode = auto
"""
