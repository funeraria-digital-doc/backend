import time
from django.utils.deprecation import MiddlewareMixin
import logging
logger = logging.getLogger(__name__)

class TimingMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        logger.info("Processing response")
        duration = time.time() - request.start_time
        message = f'{request.method} {request.path} took {duration:.2f}s to complete'
        logger.info(message)
        return response
    