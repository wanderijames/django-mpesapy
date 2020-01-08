"""HTTP call helpers"""
# pylint
import json
import urllib
from urllib.parse import urlencode


class URLFetchException(Exception):
    """Custom execption for this"""
    pass


class URLFetch:

    """Helper for calling HTTP"""

    def __init__(
            self,
            endpoint: str,
            http_method: str = "POST",
            header: dict = None,
            data: dict = None,
            **kwargs):
        """Initializes wih data for URL call

        :param endpoint: URL that will be called
        :param http_method: HTTP method to be used. Can be GET or POST
        :param header: A dictionary with key-values to pass in the HTTP header
        :param data: Data to be used in query params or body
        :type endpoint: str
        :type http_method: str
        :type header: dict
        :type data: dict or str

        """
        default_header = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        header = header or default_header
        self.http_method = http_method
        self.endpoint = endpoint
        self.content_type = header.get("Content-Type")
        if "json" in self.content_type:
            self.relay = json.dumps(data)
        elif "xml" in self.content_type:
            self.relay = data
        else:
            self.relay = urlencode(data)
        self.header = header
        self.response_headers = None
        self.options = kwargs

    def retrieve(self):
        """Does the actual calling of the endpoint provided

        :return: HTTP response as JSON, XML or str
        :warning: Will raise URLFetchException incase of HTTP error

        """
        if self.http_method == "GET":
            request = urllib.request.Request("{}?{}".format(
                self.endpoint, self.relay), headers={})
        else:
            request = urllib.request.Request(
                self.endpoint, self.relay, headers=self.header)
        try:
            start_req = urllib.request.urlopen(request)
            self.response_headers = start_req.info()
            response_code = int(start_req.code)
            response_body = start_req.read()
            if response_code == 200:
                if "return_type" in self.options:
                    return response_body
                return json.loads(response_body)
            raise URLFetchException(
                "{}: {}".format(response_code, response_body))
        except urllib.error.HTTPError as err:
            raise URLFetchException(str(err))
        except (urllib.error.URLError, Exception) as err:
            raise URLFetchException(str(err))

    def get_header(self, header_key: str) -> str:
        """Get header value by key"""
        return self.response_headers.getheader(header_key)
