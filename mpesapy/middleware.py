"""Use middleware to allow requests.

Note that this will be behind a VPN"""
# pylint: disable=too-few-public-methods
from django.http import HttpResponse
from django.urls import resolve
from django.urls.exceptions import Resolver404
from django.conf import settings


MPESA_IPS = [
    "196.201.214.136",
    "196.201.214.137",
    "196.201.214.127",
    "196.201.214.144",
    "196.201.214.145",
    "196.201.214.94",
    "196.201.214.95",
]

THIS_APP_URL_NAMES = [
    "c2b_paybill",
    "c2b_buy_goods",
    "c2b_bill",
    "c2b_till",
    "c2b_validate",
    "c2b_confirmation"
]


class IPFilterMiddleware:
    """Filter requests by IP"""

    def __init__(self):
        self.ips = getattr(settings, "MPESA_IPS", MPESA_IPS)
        self.ips.append("127.0.0.1")

    def process_request(self, request):
        """Secure the mpesa endpoints and allow requests only from mpesa"""
        path = request.path
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        remote_addr = request.META.get("REMOTE_ADDR")

        try:
            resolve_match = resolve(path)
        except Resolver404:
            return None

        if resolve_match.url_name in THIS_APP_URL_NAMES and (
                remote_addr not in self.ips and forwarded_for not in self.ips):
            return HttpResponse("Unauthorised", status=401)

        return None
