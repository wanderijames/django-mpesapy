import urllib
import urllib2
import json


class URLFetchException(Exception):
    pass


class URLFetch:

    def __init__(self, endpoint, http_method="POST",
                 header={'Content-Type': 'application/x-www-form-urlencoded'},
                 data={}, **kwargs):
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
        self.http_method = http_method
        self.endpoint = endpoint
        self.content_type = header.get("Content-Type")
        if "json" in self.content_type:
            self.relay = json.dumps(data)
        elif "xml" in self.content_type:
            self.relay = data
        else:
            self.relay = urllib.urlencode(data)
        self.header = header
        self.response_headers = None
        self.options = kwargs

    def retrieve(self):
        """Does the actual calling of the endpoint provided

        :return: HTTP response as JSON, XML or str
        :warning: Will raise URLFetchException incase of HTTP error

        """
        if self.http_method == "GET":
            request = urllib2.Request("{}?{}".format(
                self.endpoint, self.relay), headers={})
        else:
            request = urllib2.Request(
                self.endpoint, self.relay, headers=self.header)
        try:
            start_req = urllib2.urlopen(request)
            self.response_headers = start_req.info()
            response_code = int(start_req.code)
            response_body = start_req.read()
            if response_code == 200:
                if "return_type" in self.options:
                    return response_body
                return json.loads(response_body)
            raise URLFetchException(
                "{}: {}".format(response_code, response_body))
        except urllib2.HTTPError as e:
            raise URLFetchException(str(e))
        except (urllib2.URLError, Exception), e:
            raise URLFetchException(str(e))

    def get_header(self, header_key):
        return self.response_headers.getheader(header_key)
