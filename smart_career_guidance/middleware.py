"""Custom middleware for development features."""
from django.conf import settings


class DynamicCSRFMiddleware:
    """
    In DEBUG mode, automatically add the request's origin to CSRF_TRUSTED_ORIGINS.
    This allows testing from phones and other devices on the local network.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            origin = request.META.get('HTTP_ORIGIN', '')
            referer = request.META.get('HTTP_REFERER', '')
            host = request.get_host()
            
            # Build origin from host if not present
            if not origin and host:
                scheme = 'https' if request.is_secure() else 'http'
                origin = f'{scheme}://{host}'
            
            # Dynamically add to trusted origins if it's a local/private IP
            if origin:
                trusted = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
                if origin not in trusted:
                    # Only trust local/private IPs
                    if any(x in origin for x in ['127.0.0.1', 'localhost', '192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.', '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.', '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.']):
                        settings.CSRF_TRUSTED_ORIGINS = list(trusted) + [origin]
        
        return self.get_response(request)
