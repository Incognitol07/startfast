"""
Celery Generator
Generates Celery configuration for background tasks
"""

from ..base_generator import BaseGenerator


class CeleryGenerator(BaseGenerator):
    """Generates Celery configuration files"""

    def should_generate(self) -> bool:
        """Only generate if Celery is enabled"""
        return self.config.include_celery

    def generate(self):
        """Generate Celery files"""
        # Generate Celery app configuration
        celery_app_content = self._get_celery_app_template()
        self.write_file(
            f"{self.config.path}/app/tasks/celery_app.py", celery_app_content
        )

        # Generate task examples
        tasks_content = self._get_tasks_template()
        self.write_file(f"{self.config.path}/app/tasks/tasks.py", tasks_content)

        # Generate Celery worker script
        worker_script = self._get_worker_script()
        self.write_file(f"{self.config.path}/scripts/start_worker.py", worker_script)

        # Generate Celery beat configuration
        if self.config.is_advanced:
            beat_config = self._get_beat_config()
            self.write_file(f"{self.config.path}/app/tasks/beat_config.py", beat_config)

    def _get_celery_app_template(self) -> str:
        """Get Celery app configuration template"""
        template = '''"""
Celery Application Configuration
"""

from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "{project_name_snake}",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    
    # Task routing
    task_routes={{
        "app.tasks.tasks.send_email": {{"queue": "emails"}},
        "app.tasks.tasks.process_data": {{"queue": "processing"}},
        "app.tasks.tasks.generate_report": {{"queue": "reports"}},
    }},
    
    # Task execution settings
    task_always_eager=False,  # Set to True for testing
    task_eager_propagates=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,
    
    # Worker settings
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Beat schedule for periodic tasks
{beat_schedule}

# Task annotations for monitoring
celery_app.conf.task_annotations = {{
    "*": {{
        "rate_limit": "100/m",  # 100 tasks per minute
        "time_limit": 300,      # 5 minutes hard time limit
        "soft_time_limit": 240, # 4 minutes soft time limit
    }},
    "app.tasks.tasks.send_email": {{
        "rate_limit": "50/m",
        "time_limit": 60,
    }},
    "app.tasks.tasks.generate_report": {{
        "rate_limit": "10/m",
        "time_limit": 600,  # 10 minutes for reports
    }},
}}

# Error handling
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f"Request: {{self.request!r}}")
    return "Debug task completed"


# Task failure handler
@celery_app.task(bind=True)
def task_failure_handler(self, task_id, error, traceback):
    """Handle task failures"""
    print(f"Task {{task_id}} failed: {{error}}")
    # Add notification logic here (email, Slack, etc.)


# Setup task failure signals
from celery.signals import task_failure

@task_failure.connect
def on_task_failure(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwargs):
    """Handle task failure signal"""
    print(f"Task {{task_id}} failed with exception: {{exception}}")
    # Add your failure handling logic here
'''

        # Add beat schedule if advanced
        beat_schedule = ""
        if self.config.is_advanced:
            beat_schedule = """
celery_app.conf.beat_schedule = {
    "cleanup-expired-tokens": {
        "task": "app.tasks.tasks.cleanup_expired_tokens",
        "schedule": 3600.0,  # Every hour
    },
    "generate-daily-report": {
        "task": "app.tasks.tasks.generate_daily_report",
        "schedule": crontab(hour=9, minute=0),  # Every day at 9 AM
    },
    "health-check": {
        "task": "app.tasks.tasks.health_check_task",
        "schedule": 300.0,  # Every 5 minutes
    },
}

from celery.schedules import crontab"""
        else:
            beat_schedule = "# Beat schedule can be added here for periodic tasks"

        return self.format_template(template.format(beat_schedule=beat_schedule))

    def _get_tasks_template(self) -> str:
        """Get Celery tasks template"""
        template = '''"""
Celery Tasks
Background task definitions
"""

import time
import logging
from typing import Any, Dict, List, Optional
from celery import current_task
from .celery_app import celery_app
from app.core.config import settings
{additional_imports}

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={{'max_retries': 3, 'countdown': 60}})
def send_email(self, to: str, subject: str, body: str, attachment_path: Optional[str] = None):
    """
    Send email task
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body
        attachment_path: Optional path to attachment file
    """
    try:
        logger.info(f"Sending email to {{to}} with subject: {{subject}}")
        
        # Simulate email sending
        time.sleep(2)  # Replace with actual email sending logic
        
        # Example email sending implementation:
        # import smtplib
        # from email.mime.text import MIMEText
        # from email.mime.multipart import MIMEMultipart
        # 
        # msg = MIMEMultipart()
        # msg['From'] = settings.EMAIL_FROM
        # msg['To'] = to
        # msg['Subject'] = subject
        # msg.attach(MIMEText(body, 'plain'))
        # 
        # server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        # server.starttls()
        # server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        # text = msg.as_string()
        # server.sendmail(settings.EMAIL_FROM, to, text)
        # server.quit()
        
        logger.info(f"Email sent successfully to {{to}}")
        return {{"status": "success", "recipient": to}}
        
    except Exception as exc:
        logger.error(f"Failed to send email to {{to}}: {{str(exc)}}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True)
def process_data(self, data: Dict[str, Any], processing_type: str = "default"):
    """
    Process data in background
    
    Args:
        data: Data to process
        processing_type: Type of processing to perform
    """
    try:
        logger.info(f"Processing data with type: {{processing_type}}")
        
        # Update task progress
        current_task.update_state(
            state='PROGRESS',
            meta={{'current': 0, 'total': 100, 'status': 'Starting...'}}
        )
        
        # Simulate data processing
        total_steps = 10
        for i in range(total_steps):
            time.sleep(1)  # Replace with actual processing
            
            # Update progress
            current_task.update_state(
                state='PROGRESS',
                meta={{
                    'current': (i + 1) * 10,
                    'total': 100,
                    'status': f'Processing step {{i + 1}}/{{total_steps}}'
                }}
            )
        
        # Process complete
        result = {{
            "processed_data": data,
            "processing_type": processing_type,
            "timestamp": time.time(),
            "status": "completed"
        }}
        
        logger.info("Data processing completed successfully")
        return result
        
    except Exception as exc:
        logger.error(f"Data processing failed: {{str(exc)}}")
        current_task.update_state(
            state='FAILURE',
            meta={{'error': str(exc), 'status': 'Failed'}}
        )
        raise


@celery_app.task(bind=True)
def generate_report(self, report_type: str, filters: Dict[str, Any] = None):
    """
    Generate report in background
    
    Args:
        report_type: Type of report to generate
        filters: Optional filters for the report
    """
    try:
        logger.info(f"Generating {{report_type}} report")
        filters = filters or {{}}
        
        # Update task state
        current_task.update_state(
            state='PROGRESS',
            meta={{'current': 0, 'total': 100, 'status': 'Initializing report generation...'}}
        )
        
        # Simulate report generation steps
        steps = [
            "Collecting data...",
            "Processing data...",
            "Formatting report...",
            "Saving report...",
            "Sending notification..."
        ]
        
        for i, step in enumerate(steps):
            time.sleep(2)  # Replace with actual report generation logic
            
            current_task.update_state(
                state='PROGRESS',
                meta={{
                    'current': (i + 1) * 20,
                    'total': 100,
                    'status': step
                }}
            )
        
        # Generate report file path
        report_filename = f"{{report_type}}_report_{{int(time.time())}}.pdf"
        report_path = f"/reports/{{report_filename}}"
        
        # Simulate report file creation
        # In real implementation, generate actual report file
        
        result = {{
            "report_type": report_type,
            "filename": report_filename,
            "file_path": report_path,
            "filters": filters,
            "generated_at": time.time(),
            "status": "completed"
        }}
        
        logger.info(f"Report generated successfully: {{report_filename}}")
        return result
        
    except Exception as exc:
        logger.error(f"Report generation failed: {{str(exc)}}")
        raise


@celery_app.task
def cleanup_expired_tokens():
    """Clean up expired authentication tokens"""
    try:
        logger.info("Starting token cleanup task")
        
        # Add token cleanup logic here
        # Example:
        # from app.services.auth_service import cleanup_expired_tokens
        # deleted_count = cleanup_expired_tokens()
        
        deleted_count = 0  # Placeholder
        
        logger.info(f"Token cleanup completed. Deleted {{deleted_count}} expired tokens")
        return {{"deleted_count": deleted_count, "status": "completed"}}
        
    except Exception as exc:
        logger.error(f"Token cleanup failed: {{str(exc)}}")
        raise


@celery_app.task
def health_check_task():
    """Health check task for monitoring"""
    try:
        # Perform health checks
        checks = {{
            "database": "healthy",  # Add actual database check
            "redis": "healthy",     # Add actual Redis check
            "disk_space": "healthy", # Add disk space check
            "memory": "healthy"     # Add memory check
        }}
        
        logger.info("Health check completed successfully")
        return {{"checks": checks, "status": "healthy", "timestamp": time.time()}}
        
    except Exception as exc:
        logger.error(f"Health check failed: {{str(exc)}}")
        return {{"status": "unhealthy", "error": str(exc), "timestamp": time.time()}}


@celery_app.task
def generate_daily_report():
    """Generate daily report (scheduled task)"""
    try:
        logger.info("Generating daily report")
        
        # Generate daily statistics
        report_data = {{
            "date": time.strftime("%Y-%m-%d"),
            "total_users": 0,    # Add actual user count
            "total_items": 0,    # Add actual item count
            "api_requests": 0,   # Add actual API request count
            "errors": 0          # Add actual error count
        }}
        
        # Send report via email (example)
        send_email.delay(
            to="admin@{project_name_snake}.com",
            subject=f"Daily Report - {{report_data['date']}}",
            body=f"Daily report data: {{report_data}}"
        )
        
        logger.info("Daily report generated and sent")
        return report_data
        
    except Exception as exc:
        logger.error(f"Daily report generation failed: {{str(exc)}}")
        raise


{ml_tasks}

{additional_tasks}


# Task utility functions

def get_task_status(task_id: str):
    """Get task status by ID"""
    result = celery_app.AsyncResult(task_id)
    return {{
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "info": result.info
    }}


def cancel_task(task_id: str):
    """Cancel a running task"""
    celery_app.control.revoke(task_id, terminate=True)
    return {{"task_id": task_id, "status": "cancelled"}}


def get_active_tasks():
    """Get list of active tasks"""
    inspect = celery_app.control.inspect()
    active_tasks = inspect.active()
    return active_tasks


def get_worker_stats():
    """Get worker statistics"""
    inspect = celery_app.control.inspect()
    stats = inspect.stats()
    return stats
'''

        # Add ML-specific tasks if ML API
        ml_tasks = ""
        if self.config.project_type.value == "ml-api":
            ml_tasks = '''
@celery_app.task(bind=True)
def train_model(self, training_data: Dict[str, Any], model_config: Dict[str, Any]):
    """
    Train ML model in background
    
    Args:
        training_data: Data for training
        model_config: Model configuration parameters
    """
    try:
        logger.info("Starting model training")
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Preparing training data...'}
        )
        
        # Simulate training steps
        training_steps = [
            "Loading training data...",
            "Preprocessing data...",
            "Training model...",
            "Validating model...",
            "Saving model..."
        ]
        
        for i, step in enumerate(training_steps):
            time.sleep(5)  # Replace with actual training logic
            
            current_task.update_state(
                state='PROGRESS',
                meta={{
                    'current': (i + 1) * 20,
                    'total': 100,
                    'status': step
                }}
            )
        
        # Training complete
        result = {{
            "model_id": f"model_{{int(time.time())}}",
            "accuracy": 0.95,  # Placeholder
            "training_time": 25,  # Placeholder
            "status": "completed"
        }}
        
        logger.info("Model training completed successfully")
        return result
        
    except Exception as exc:
        logger.error(f"Model training failed: {{str(exc)}}")
        raise


@celery_app.task(bind=True)
def batch_predict(self, input_data: List[Dict[str, Any]], model_id: str):
    """
    Perform batch predictions
    
    Args:
        input_data: List of input data for predictions
        model_id: ID of the model to use
    """
    try:
        logger.info(f"Starting batch prediction with model {{model_id}}")
        
        total_items = len(input_data)
        predictions = []
        
        for i, data in enumerate(input_data):
            # Simulate prediction
            time.sleep(0.1)  # Replace with actual prediction
            
            prediction = {{
                "input": data,
                "prediction": "sample_result",  # Placeholder
                "confidence": 0.9  # Placeholder
            }}
            predictions.append(prediction)
            
            # Update progress
            current_task.update_state(
                state='PROGRESS',
                meta={{
                    'current': i + 1,
                    'total': total_items,
                    'status': f'Processed {{i + 1}}/{{total_items}} predictions'
                }}
            )
        
        result = {{
            "predictions": predictions,
            "model_id": model_id,
            "total_processed": total_items,
            "status": "completed"
        }}
        
        logger.info(f"Batch prediction completed. Processed {{total_items}} items")
        return result
        
    except Exception as exc:
        logger.error(f"Batch prediction failed: {{str(exc)}}")
        raise
'''

        # Additional imports for ML tasks
        additional_imports = ""
        if self.config.project_type.value == "ml-api":
            additional_imports = (
                "# from app.services.prediction_service import batch_predict_service"
            )

        # Additional task examples
        additional_tasks = '''
# Example: File processing task
@celery_app.task(bind=True)
def process_uploaded_file(self, file_path: str, file_type: str):
    """Process uploaded file"""
    try:
        logger.info(f"Processing file: {{file_path}}")
        
        # Add file processing logic here
        # Example: image resizing, document parsing, etc.
        
        return {{"file_path": file_path, "status": "processed"}}
        
    except Exception as exc:
        logger.error(f"File processing failed: {{str(exc)}}")
        raise


# Example: Notification task
@celery_app.task
def send_push_notification(user_id: int, title: str, message: str):
    """Send push notification to user"""
    try:
        logger.info(f"Sending push notification to user {{user_id}}")
        
        # Add push notification logic here
        # Example: Firebase, APNs, etc.
        
        return {{"user_id": user_id, "status": "sent"}}
        
    except Exception as exc:
        logger.error(f"Push notification failed: {{str(exc)}}")
        raise
'''

        return self.format_template(
            template.format(
                additional_imports=additional_imports,
                ml_tasks=ml_tasks,
                additional_tasks=additional_tasks,
            )
        )

    def _get_worker_script(self) -> str:
        """Get Celery worker startup script"""
        template = '''#!/usr/bin/env python3
"""
Celery Worker Startup Script
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.tasks.celery_app import celery_app

if __name__ == "__main__":
    # Start Celery worker
    celery_app.start([
        "worker",
        "--loglevel=info",
        "--concurrency=4",
        "--hostname=worker@%h",
        "--queues=celery,emails,processing,reports",
        "--prefetch-multiplier=1",
        "--max-tasks-per-child=1000",
    ])
'''

        return self.format_template(template)

    def _get_beat_config(self) -> str:
        """Get Celery beat configuration"""
        template = '''"""
Celery Beat Schedule Configuration
Periodic task scheduling
"""

from celery.schedules import crontab
from .celery_app import celery_app

# Periodic task schedule
CELERY_BEAT_SCHEDULE = {{
    # Cleanup tasks
    "cleanup-expired-tokens": {{
        "task": "app.tasks.tasks.cleanup_expired_tokens",
        "schedule": crontab(minute=0),  # Every hour
        "options": {{"queue": "cleanup"}}
    }},
    
    # Daily reports
    "generate-daily-report": {{
        "task": "app.tasks.tasks.generate_daily_report",
        "schedule": crontab(hour=9, minute=0),  # Every day at 9 AM
        "options": {{"queue": "reports"}}
    }},
    
    # Health monitoring
    "health-check": {{
        "task": "app.tasks.tasks.health_check_task",
        "schedule": 300.0,  # Every 5 minutes
        "options": {{"queue": "monitoring"}}
    }},
    
    # Weekly maintenance
    "weekly-maintenance": {{
        "task": "app.tasks.tasks.weekly_maintenance",
        "schedule": crontab(hour=2, minute=0, day_of_week=1),  # Monday 2 AM
        "options": {{"queue": "maintenance"}}
    }},
    
    # Database optimization
    "optimize-database": {{
        "task": "app.tasks.tasks.optimize_database",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),  # Sunday 3 AM
        "options": {{"queue": "maintenance"}}
    }},
    
    {ml_schedule}
    
    {custom_schedule}
}}

# Apply the schedule to Celery app
celery_app.conf.beat_schedule = CELERY_BEAT_SCHEDULE
celery_app.conf.timezone = "UTC"

# Additional beat configuration
celery_app.conf.beat_schedule_filename = "celerybeat-schedule"
celery_app.conf.beat_max_loop_interval = 300  # 5 minutes


def add_periodic_task(name: str, task: str, schedule, **kwargs):
    """
    Dynamically add a periodic task
    
    Args:
        name: Unique name for the task
        task: Task function name
        schedule: Schedule (crontab or number for interval)
        **kwargs: Additional options
    """
    CELERY_BEAT_SCHEDULE[name] = {{
        "task": task,
        "schedule": schedule,
        **kwargs
    }}
    celery_app.conf.beat_schedule = CELERY_BEAT_SCHEDULE


def remove_periodic_task(name: str):
    """Remove a periodic task by name"""
    if name in CELERY_BEAT_SCHEDULE:
        del CELERY_BEAT_SCHEDULE[name]
        celery_app.conf.beat_schedule = CELERY_BEAT_SCHEDULE


def list_periodic_tasks():
    """List all periodic tasks"""
    return list(CELERY_BEAT_SCHEDULE.keys())


# Example usage:
# add_periodic_task(
#     "custom-task",
#     "app.tasks.tasks.custom_task",
#     crontab(hour=12, minute=0),
#     options={{"queue": "custom"}}
# )
'''

        # Add ML-specific scheduled tasks
        ml_schedule = ""
        if self.config.project_type.value == "ml-api":
            ml_schedule = """
    # Model retraining
    "retrain-model": {
        "task": "app.tasks.tasks.retrain_model",
        "schedule": crontab(hour=1, minute=0, day_of_week=1),  # Weekly
        "options": {"queue": "ml-training"}
    },
    
    # Model validation
    "validate-models": {
        "task": "app.tasks.tasks.validate_all_models",
        "schedule": crontab(hour=4, minute=0),  # Daily at 4 AM
        "options": {"queue": "ml-validation"}
    },"""

        # Custom schedule placeholder
        custom_schedule = """
    # Add your custom scheduled tasks here
    # "custom-task": {
    #     "task": "app.tasks.tasks.custom_task",
    #     "schedule": crontab(hour=0, minute=0),
    #     "options": {"queue": "custom"}
    # },"""

        return self.format_template(
            template.format(ml_schedule=ml_schedule, custom_schedule=custom_schedule)
        )


# Create the scripts directory __init__.py
scripts_init_content = '''"""
Scripts Package
Utility scripts for the application
"""'''
