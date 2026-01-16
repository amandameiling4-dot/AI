"""Integration of monitoring into the FastAPI server."""
from fastapi import FastAPI
from backend.monitoring.logging_config import logger
from backend.monitoring.metrics import MetricsCollector
from backend.monitoring.prometheus_metrics import export_metrics, inference_requests, inference_latency, tokens_generated, api_errors
import time


def add_monitoring_middleware(app: FastAPI):
    """Add monitoring middleware to FastAPI app."""
    
    metrics_collector = MetricsCollector()

    @app.middleware('http')
    async def monitoring_middleware(request, call_next):
        """Log and track all requests."""
        start_time = time.time()
        
        # Get API key if available
        auth_header = request.headers.get('Authorization', '')
        api_key = auth_header.replace('Bearer ', '') if auth_header else 'unknown'
        
        logger.info(f'{request.method} {request.url.path}')
        
        try:
            response = await call_next(request)
            
            latency_ms = (time.time() - start_time) * 1000
            status = 'success' if 200 <= response.status_code < 300 else 'error'
            
            # Record metrics
            inference_requests.labels(status=status, model='api').inc()
            inference_latency.labels(model='api').observe(time.time() - start_time)
            
            logger.info(f'{request.method} {request.url.path} - {response.status_code} - {latency_ms:.2f}ms')
            return response
        except Exception as e:
            logger.error(f'Request failed: {e}', exc_info=True)
            api_errors.labels(error_type=type(e).__name__).inc()
            raise

    @app.get('/metrics')
    async def get_metrics():
        """Prometheus metrics endpoint."""
        return export_metrics()

    return app
