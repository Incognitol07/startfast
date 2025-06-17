"""
Utils Generator
Generates utility functions and helpers
"""

from ..base_generator import BaseGenerator


class UtilsGenerator(BaseGenerator):
    """Generates utility files"""

    def generate(self):
        """Generate utility files"""
        # Generate common utilities
        utils_content = self._get_utils_template()
        self.write_file(f"{self.config.path}/app/utils/helpers.py", utils_content)

        # Generate logging utilities
        logging_content = self.format_template(self._get_logging_template())
        self.write_file(
            f"{self.config.path}/app/utils/logging.py", logging_content
        )  # Generate validation utilities
        validation_content = self._get_validation_template()
        self.write_file(
            f"{self.config.path}/app/utils/validation.py", validation_content
        )

    def _get_utils_template(self) -> str:
        """Get general utilities template"""
        template = r'''
"""
Utility Functions
Common helper functions used across the application
"""

import re
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid.uuid4())


def generate_hash(data: str, algorithm: str = "sha256") -> str:
    """Generate hash for given data"""
    hash_func = getattr(hashlib, algorithm)
    return hash_func(data.encode()).hexdigest()


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime string"""
    return datetime.strptime(dt_str, format_str)


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_divide(numerator: Union[int, float], denominator: Union[int, float]) -> Optional[float]:
    """Safely divide two numbers, returning None if division by zero"""
    try:
        return numerator / denominator if denominator != 0 else None
    except (TypeError, ZeroDivisionError):
        return None


def flatten_dict(data: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """Flatten nested dictionary"""
    items = []
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def remove_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary"""
    return {k: v for k, v in data.items() if v is not None}


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_file_content(file_path: Union[str, Path], encoding: str = "utf-8") -> str:
    """Read file content safely"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")


def write_file_content(file_path: Union[str, Path], content: str, encoding: str = "utf-8") -> bool:
    """Write content to file safely"""
    try:
        ensure_directory(Path(file_path).parent)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)        
            return True
    except Exception as e:
        raise Exception(f"Error writing file {file_path}: {e}")
'''

        return template

    def _get_logging_template(self) -> str:
        """Get logging utilities template"""
        template = '''
"""
Logging Utilities
Enhanced logging functionality
"""

import logging
import sys
from typing import Any, Dict, Optional
from pathlib import Path
from app.core.config import settings


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output"""
    
    COLORS = {{
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red        
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }}
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Add color to level name
        record.levelname = f"{{log_color}}{{record.levelname}}{{reset_color}}"
        
        return super().format(record)


def setup_logging() -> logging.Logger:
    """Set up application logging"""
    logger = logging.getLogger("{project_name_snake}")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler if log file is specified
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get logger instance"""
    if name is None:
        name = "{project_name_snake}"
    return logging.getLogger(name)


def log_function_call(func_name: str, args: tuple = (), kwargs: dict = None) -> None:
    """Log function call with parameters"""
    logger = get_logger()
    kwargs = kwargs or {{}}
    
    params = []
    if args:
        params.extend([str(arg) for arg in args])
    if kwargs:
        params.extend([f"{{k}}={{v}}" for k, v in kwargs.items()])
    
    params_str = ", ".join(params)
    logger.debug(f"Calling {{func_name}}({{params_str}})")


def log_execution_time(func_name: str, execution_time: float) -> None:
    """Log function execution time"""
    logger = get_logger()
    logger.info(f"{{func_name}} executed in {{execution_time:.4f}} seconds")


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log error with context"""
    logger = get_logger()
    context = context or {{}}
    
    error_msg = f"Error: {{type(error).__name__}}: {{str(error)}}"
    if context:
        error_msg += f" | Context: {{context}}"
    
    logger.error(error_msg, exc_info=True)


# Global logger instance
app_logger = setup_logging()
'''

        return template

    def _get_validation_template(self) -> str:
        """Get validation utilities template"""
        template = r'''
"""
Validation Utilities
Common validation functions
"""

import re
from typing import Any, Dict, List, Optional, Union
from pydantic import ValidationError


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove non-digit characters
    cleaned = re.sub(r'\D', '', phone)
    # Check if it has 10-15 digits
    return 10 <= len(cleaned) <= 15


def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))


def is_strong_password(password: str) -> bool:
    """Check if password meets strength requirements"""
    if len(password) < 8:
        return False
    
    # Check for at least one lowercase, uppercase, digit, and special character
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    return all([has_lower, has_upper, has_digit, has_special])


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate that required fields are present and not empty"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    return missing_fields


def validate_data_types(data: Dict[str, Any], type_mapping: Dict[str, type]) -> List[str]:
    """Validate data types for given fields"""
    type_errors = []
    
    for field, expected_type in type_mapping.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                type_errors.append(f"{field} must be of type {expected_type.__name__}")
    
    return type_errors


def validate_string_length(
    text: str, 
    min_length: Optional[int] = None, 
    max_length: Optional[int] = None
) -> bool:
    """Validate string length"""
    if min_length is not None and len(text) < min_length:
        return False
    if max_length is not None and len(text) > max_length:
        return False
    return True


def validate_numeric_range(
    value: Union[int, float], 
    min_value: Optional[Union[int, float]] = None, 
    max_value: Optional[Union[int, float]] = None
) -> bool:
    """Validate numeric value is within range"""
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def sanitize_string(text: str, allow_html: bool = False) -> str:
    """Sanitize string input"""
    if not allow_html:
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
    
    # Remove or escape potentially dangerous characters
    text = text.replace('\\', '\\\\')
    text = text.replace('\x00', '')  # Remove null bytes
    
    return text.strip()


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension"""
    if not filename:
        return False
    
    extension = filename.lower().split('.')[-1]
    return extension in [ext.lower() for ext in allowed_extensions]


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Basic JSON schema validation"""
    errors = []
    
    # Check required fields
    if 'required' in schema:
        missing = validate_required_fields(data, schema['required'])
        errors.extend([f"Missing required field: {field}" for field in missing])
    
    # Check properties
    if 'properties' in schema:
        for field, field_schema in schema['properties'].items():
            if field in data:
                value = data[field]
                
                # Type validation
                if 'type' in field_schema:
                    expected_type = field_schema['type']
                    if expected_type == 'string' and not isinstance(value, str):
                        errors.append(f"{field} must be a string")
                    elif expected_type == 'integer' and not isinstance(value, int):
                        errors.append(f"{field} must be an integer")
                    elif expected_type == 'number' and not isinstance(value, (int, float)):
                        errors.append(f"{field} must be a number")
                    elif expected_type == 'boolean' and not isinstance(value, bool):
                        errors.append(f"{field} must be a boolean")
                
                # String length validation
                if isinstance(value, str) and 'minLength' in field_schema:
                    if len(value) < field_schema['minLength']:
                        errors.append(f"{field} must be at least {field_schema['minLength']} characters")
                
                if isinstance(value, str) and 'maxLength' in field_schema:
                    if len(value) > field_schema['maxLength']:
                        errors.append(f"{field} must be at most {field_schema['maxLength']} characters")
    
    return errors


class ValidationResult:
    """Validation result container"""
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_errors(self, errors: List[str]):
        """Add multiple validation errors"""
        self.errors.extend(errors)
        if errors:
            self.is_valid = False
    
    def __bool__(self):
        return self.is_valid
    
    def __str__(self):
        if self.is_valid:
            return "Validation passed"        
        return f"Validation failed: {', '.join(self.errors)}"
'''

        return template
