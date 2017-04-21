import logging
from django.http import HttpResponse
from django.conf import settings

logger = logging.getLogger(__name__)


class IPFilterMiddleware(object):
    def __init__(self):
        self.ips = ("196.201.214.136", "196.201.214.137", "196.201.214.127",
                    "196.201.214.144", "196.201.214.145", "196.201.214.94",
                    "196.201.214.95", "127.0.0.1")
        self.mpesa_only_paths = ("/v2/validate", "/v2/confirm",
                                 "/v1/c2b_bill", "/v1/c2b_buy",
                                 "/c2b_bill", "/c2b_buy")
        self.server_name = getattr(settings, "MY_SERVER_NAME", "xyz")

    def process_request(self, request):
        path = request.path
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        remote_addr = request.META.get("REMOTE_ADDR")
        is_path = filter(lambda x: path.startswith(x), self.mpesa_only_paths)
        if is_path and (remote_addr not in self.ips and
                        forwarded_for not in self.ips):
            return HttpResponse("Unauthorised", status=401)

        return None
