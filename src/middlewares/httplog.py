import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from logging import getLogger

# Create a logger for HTTP requests
request_logger = getLogger('request_logger')

class LogRequestsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_time = time.time()
        response = await call_next(request)
        process_time = time.time() - request_time
        formatted_process_time = f'{process_time:.4f}'
        
        # Get the client's IP address
        client_ip = request.client.host

        request_logger.info(
            f"{request.method} {request.url.path} - Status: {response.status_code} - Time: {formatted_process_time}s - IP: {client_ip} - user-agent: {request.headers.get("User-Agent", "")}"
        )

        return response
