"""
Monitoring Generator
Generates monitoring and observability files
"""

from ..base_generator import BaseGenerator


class MonitoringGenerator(BaseGenerator):
    """Generates monitoring configuration files"""

    def should_generate(self) -> bool:
        """Only generate if monitoring is enabled"""
        return self.config.include_monitoring

    def generate(self):
        """Generate monitoring files"""
        # Generate Prometheus configuration
        prometheus_config = self._get_prometheus_config()
        self.write_file(
            f"{self.config.path}/monitoring/prometheus.yml", prometheus_config
        )

        # Generate Grafana dashboard
        grafana_dashboard = self._get_grafana_dashboard()
        self.write_file(
            f"{self.config.path}/monitoring/grafana/dashboard.json", grafana_dashboard
        )

        # Generate monitoring middleware
        monitoring_middleware = self._get_monitoring_middleware()
        self.write_file(
            f"{self.config.path}/app/utils/monitoring.py", monitoring_middleware
        )

    def _get_prometheus_config(self) -> str:
        """Get Prometheus configuration"""
        template = """# Prometheus configuration for {project_name_pascal}
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: '{project_name_snake}-api'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: '{project_name_snake}-health'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/health'
    scrape_interval: 10s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          # - alertmanager:9093
"""

        return self.format_template(template)

    def _get_grafana_dashboard(self) -> str:
        """Get Grafana dashboard configuration"""
        template = """{{
  "dashboard": {{
    "id": null,
    "title": "{project_name_pascal} Monitoring Dashboard",
    "tags": ["fastapi", "{project_name_snake}"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {{
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {{
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }}
        ],
        "yAxes": [
          {{
            "label": "requests/sec"
          }}
        ],
        "xAxes": [
          {{
            "mode": "time"
          }}
        ],
        "gridPos": {{
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 0
        }}
      }},
      {{
        "id": 2,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {{
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }},
          {{
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }}
        ],
        "yAxes": [
          {{
            "label": "seconds"
          }}
        ],
        "xAxes": [
          {{
            "mode": "time"
          }}
        ],
        "gridPos": {{
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 0
        }}
      }},
      {{
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {{
            "expr": "rate(http_requests_total{{status=~\"4..|5..\"}}[5m])",
            "legendFormat": "Error rate"
          }}
        ],
        "yAxes": [
          {{
            "label": "errors/sec"
          }}
        ],
        "xAxes": [
          {{
            "mode": "time"
          }}
        ],
        "gridPos": {{
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 8
        }}
      }},
      {{
        "id": 4,
        "title": "Active Connections",
        "type": "singlestat",
        "targets": [
          {{
            "expr": "http_requests_active",
            "legendFormat": "Active"
          }}
        ],
        "gridPos": {{
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 8
        }}
      }}
    ],
    "time": {{
      "from": "now-1h",
      "to": "now"
    }},
    "refresh": "5s"
  }}
}}"""

        return self.format_template(template)

    def _get_monitoring_middleware(self) -> str:
        """Get monitoring middleware"""
        template = '''"""
Monitoring and Metrics Middleware
"""

import time
from typing import Callable
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import structlog

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Number of active HTTP requests'
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

# Structured logger
logger = structlog.get_logger()


class MonitoringMiddleware:
    """Middleware for monitoring and metrics collection"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        start_time = time.time()
        
        # Increment active requests
        ACTIVE_REQUESTS.inc()
        
        try:
            # Process request
            response = await self._process_request(request, start_time)
            
            # Send response
            await response(scope, receive, send)
            
        except Exception as e:
            # Log error
            logger.error(
                "Request processing error",
                method=request.method,
                url=str(request.url),
                error=str(e),
                exc_info=True
            )
            
            # Record error metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status="500"
            ).inc()
            
            raise
        
        finally:
            # Decrement active requests
            ACTIVE_REQUESTS.dec()
    
    async def _process_request(self, request: Request, start_time: float):
        """Process the request and collect metrics"""
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            user_agent=request.headers.get("user-agent"),
            remote_addr=request.client.host if request.client else None
        )
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.time() - start_time
                
                # Record metrics
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=str(status_code)
                ).inc()
                
                REQUEST_DURATION.labels(
                    method=request.method,
                    endpoint=request.url.path
                ).observe(duration)
                
                # Log response
                logger.info(
                    "Request completed",
                    method=request.method,
                    url=str(request.url),
                    status_code=status_code,
                    duration=f"{{duration:.4f}}s"
                )
            
            await send(message)
        
        # Create response
        response = await self.app(request.scope, request.receive, send_wrapper)
        return response


def get_metrics():
    """Get Prometheus metrics"""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


class HealthCheck:
    """Health check utility"""
    
    def __init__(self):
        self.start_time = time.time()
    
    async def get_health(self):
        """Get application health status"""
        uptime = time.time() - self.start_time
        
        # Basic health check
        health_status = {{
            "status": "healthy",
            "uptime": f"{{uptime:.2f}} seconds",
            "version": "1.0.0",
            "environment": "development",  # From config
            "timestamp": time.time()
        }}
        
        # Add detailed checks if needed
        health_status.update(await self._detailed_health_check())
        
        return health_status
    
    async def _detailed_health_check(self):
        """Perform detailed health checks"""
        checks = {{}}
        
        # Database health check
        try:
            # Add database ping here
            checks["database"] = "healthy"
        except Exception as e:
            checks["database"] = f"unhealthy: {{str(e)}}"
        
        # External service checks
        # Add checks for external dependencies
        
        return checks


# Global health checker
health_checker = HealthCheck()


def setup_monitoring(app):
    """Set up monitoring for the FastAPI app"""
    
    # Add middleware
    app.add_middleware(MonitoringMiddleware)
    
    # Add metrics endpoint
    @app.get("/metrics")
    async def metrics():
        return get_metrics()
    
    # Enhanced health check
    @app.get("/health")
    async def health():
        return await health_checker.get_health()
    
    logger.info("Monitoring setup completed")


# Custom metrics for business logic
BUSINESS_METRICS = {{
    'items_created': Counter('items_created_total', 'Total number of items created'),
    'items_updated': Counter('items_updated_total', 'Total number of items updated'),
    'items_deleted': Counter('items_deleted_total', 'Total number of items deleted'),
    'login_attempts': Counter('login_attempts_total', 'Total login attempts', ['status']),
}}


def track_business_metric(metric_name: str, labels: dict = None, value: float = 1):
    """Track business-specific metrics"""
    if metric_name in BUSINESS_METRICS:
        metric = BUSINESS_METRICS[metric_name]
        if labels:
            metric.labels(**labels).inc(value)
        else:
            metric.inc(value)
    else:
        logger.warning(f"Unknown business metric: {{metric_name}}")


# Performance monitoring decorator
def monitor_performance(metric_name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"Function {{func.__name__}} completed",
                    duration=f"{{duration:.4f}}s",
                    metric_name=metric_name
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Function {{func.__name__}} failed",
                    duration=f"{{duration:.4f}}s",
                    error=str(e),
                    metric_name=metric_name
                )
                raise
        
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"Function {{func.__name__}} completed",
                    duration=f"{{duration:.4f}}s",
                    metric_name=metric_name
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Function {{func.__name__}} failed",
                    duration=f"{{duration:.4f}}s",
                    error=str(e),
                    metric_name=metric_name
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
'''

        return self.format_template(template)
