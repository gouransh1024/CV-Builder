"""Custom middleware for development and network testing features."""
import ipaddress
import urllib.parse
from django.conf import settings


def _is_safe_local_origin(origin: str) -> bool:
    """
    Strictly validate that an origin is localhost or a private local IPv4 address.
    Rejects attacker hostnames with substring matches (e.g. localhost.evil.com).
    """
    if not origin:
        return False
    try:
        parsed = urllib.parse.urlsplit(origin)
        hostname = parsed.hostname
        if not hostname:
            return False
        if hostname in ("localhost", "127.0.0.1"):
            return True
        # Check for RFC 1918 private IP address
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback
    except Exception:
        return False


class DynamicCSRFMiddleware:
    """
    In DEBUG mode, automatically add legitimate local network IPs to CSRF_TRUSTED_ORIGINS.
    This safely allows mobile testing over local Wi-Fi without exposing CSRF to external domains.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, 'DEBUG', False):
            origin = request.META.get('HTTP_ORIGIN', '')
            host = request.get_host()

            if not origin and host:
                scheme = 'https' if request.is_secure() else 'http'
                origin = f'{scheme}://{host}'

            if origin and _is_safe_local_origin(origin):
                trusted = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
                if origin not in trusted:
                    settings.CSRF_TRUSTED_ORIGINS = list(trusted) + [origin]

        return self.get_response(request)
