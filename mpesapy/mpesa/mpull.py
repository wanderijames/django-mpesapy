import re
import ast
import httplib
import json
import xml2dict

httplib.HTTPConnection.debuglevel = 0


class PullError(Exception):
    """Exception to be raised in this module"""
    pass


class MpesaPull:
    """Pull request interfaces for confirming the push IPN from M-Pesa."""

    def __init__(self, user, password, terminal_msisdn):
        """Initialize the object with the required inputs.

        Args:
            user(str): The username that you provided and configured with M-Pesa.
            user(str): The password that you provided and configured with M-Pesa.
            terminal_msisdn(str): Number in the format 2547xxxxxxxx that M-Pesa provided as termial msisdn."""
        self.user = user
        self.password = password
        self.terminal_msisdn = terminal_msisdn
        self.xml = '''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:ipn="http://ipn/">
    <soapenv:Header/>
    <soapenv:Body>
        <ipn:retrieveTransaction>
            <transactionCode>{transaction_code}</transactionCode>
            <senderMsisdn>{sender_msisdn}</senderMsisdn>
            <terminalMsisdn>{terminal_msisdn}</terminalMsisdn>
            <password>{password}</password>
        </ipn:retrieveTransaction>
    </soapenv:Body>
</soapenv:Envelope>'''.format(password=password, terminal_msisdn=terminal_msisdn)

    def _search_tag(self, root="ack", xml2search=None):
        sample_local_response = str(xml2search).replace("\n", "").strip() if xml2search is not None else \
            str(self.xml2search).replace("\n", "").strip()

        st = re.finditer(root, sample_local_response)
        if st is not None:
            start = 9999999999999
            end = 0
            for i in st:
                sp = i.span()
                start = min(start, sp[1])
                end = max(end, sp[0])
            st = re.search(">", sample_local_response[start:])
            if st is not None:
                start += st.span()[1]
            return sample_local_response[start:end - 2].strip()

    def _soap_request(self, soap_action="/IPNWeb/IpnWebRetrieval?wsdl"):
        """Handles making the SOAP request to the Safaricom M-Pesa Soap server

        Args:
            str(Optional): URI denoting the Soap action

        Returns:
            dict: Containing transaction details otherwise empty

        Raises:
            PullError incase the HTTP connection has returned HTTP response other than 200

        """

        data = self.xml

        webservice = httplib.HTTPSConnection("www.safaricom.co.ke", 443)
        webservice.putrequest("POST", "/IPN/IpnWebRetrieval?wsdl")
        webservice.putheader("Host", "www.safaricom.co.ke")
        webservice.putheader("User-Agent", "Python 2.7 CMT")
        webservice.putheader("Content-type", 'application/soap+xml; charset=utf-8')
        webservice.putheader("Content-length", "%d" % len(data))
        webservice.putheader("SOAPAction", soap_action)
        webservice.endheaders()
        webservice.send(data)

        response = webservice.getresponse()
        cont = response.read()
        if response.status == 500:
            raise PullError("{}:{}".format(
                self._search_tag('faultcode', cont),
                self._search_tag('faultstring', cont)))
        elif response.status != 200:
            raise PullError("{}: {}".format(response.cont))
        else:
            trans = self._search_tag('ns2:retrieveTransactionResponse', cont)
            if len(trans) > 0:
                o = xml2dict.parse(trans)
                js = ast.literal_eval(json.dumps(o))
                return js.get('transaction')
        return {}

    def counter_check(self, transaction_code, sender_msisdn):
        self.xml = self.xml.format(transaction_code=transaction_code,
                                   sender_msisdn=sender_msisdn)
        return self._SOAP_Post()
