"""Helper classes for onlne"""
# pylint: disable=unused-argument
import xml.etree.ElementTree as ET
try:
    from suds.client import Client  # find a suitable library
except ImportError:
    pass

from .utils import encrypt_password


class OnlineCheckout:
    """Wrapper class for online checkout"""

    merchant_transaction_id = None
    reference_id = None
    amount = 0.0
    enc_params = None
    callback_url = None
    callback_method = "xml"
    checkout_wsdl = "https://www.safaricom.co.ke/mpesa_online/lnmo_checkout_server.php?wsdl"  # noqa

    def __init__(self, **kwargs):
        for k in kwargs:
            try:
                getattr(self, "set_{}".format(k))(kwargs[k])
            except AttributeError:
                pass

    def set_merchant_transaction_id(self, transaction_id):
        """Sets the value of merchant transaction id"""
        self.merchant_transaction_id = transaction_id

    def set_reference_id(self, reference_id):
        """Sets the value of reference id"""
        self.reference_id = reference_id

    def set_amount(self, amount):
        """Sets the value of amount"""
        self.amount = amount

    def set_enc_params(self, enc_params):
        """Sets the value of encrypted params"""
        self.enc_params = enc_params

    def set_callback_url(self, callback_url):
        """Sets the value of callback url"""
        self.callback_url = callback_url

    def set_callback_method(self, callback_method):
        """Sets the value of callback method"""
        self.callback_method = callback_method

    def process_checkout_request(
            self, merchant_id, pass_key, msisdn):
        """Send checkout request"""
        timestamp, password = encrypt_password(merchant_id, pass_key)
        client = Client(self.checkout_wsdl)
        checkout_header = client.factory.create("CheckOutHeader")
        checkout_header.MERCHANT_ID = merchant_id
        checkout_header.PASSWORD = password
        checkout_header.TIMESTAMP = timestamp
        client.set_options(soap_headers=checkout_header)
        result = client.service.processCheckOut(
            MERCHANT_TRANSACTION_ID=self.merchant_transaction_id,
            REFERENCE_ID=self.reference_id,
            AMOUNT=self.amount,
            MSISDN=msisdn,
            ENC_PARAMS=self.enc_params,
            CALL_BACK_URL=self.callback_url,
            CALL_BACK_METHOD=self.callback_method,
            TIMESTAMP=timestamp)
        return result

    @staticmethod
    def process_checkout_response(response) -> dict:
        """Process response from checkout request"""
        result = {}
        root = ET.fromstring(response)
        namespace_ = {
            "SOAP-ENV": "http://schemas.xmlsoap.org/soap/envelope/",
            "ns1": "tns:ns"}
        for child in root.findall("SOAP-ENV:Body", namespace_):
            checkout_element = child.find(
                "ns1:processCheckOutResponse", namespace_)
            result["status_code"] = checkout_element.find("RETURN_CODE").text
            result["desc"] = checkout_element.find("DESCRIPTION").text
            result["trans_id"] = checkout_element.find("TRX_ID").text
            result["message"] = checkout_element.find("CUST_MSG").text

        return result

    def confirm_transaction_request(
            self, merchant_id, pass_key, reference_id, msisdn):
        """Send a confirmation request"""
        timestamp, password = encrypt_password(merchant_id, pass_key)
        client = Client(self.checkout_wsdl)
        checkout_header = client.factory.create("CheckOutHeader")
        checkout_header.MERCHANT_ID = merchant_id
        checkout_header.PASSWORD = password
        checkout_header.TIMESTAMP = timestamp
        client.set_options(soap_headers=checkout_header)
        result = client.service.confirmTransaction(
            MERCHANT_TRANSACTION_ID=self.merchant_transaction_id,
            TRX_ID=msisdn)
        return result

    @staticmethod
    def confirm_transaction_response(response) -> dict:
        """Process response of confirmation request"""
        result = {}
        root = ET.fromstring(response)
        namespace_ = {
            "SOAP-ENV": "http://schemas.xmlsoap.org/soap/envelope/",
            "ns1": "tns:ns"}
        for child in root.findall("SOAP-ENV:Body", namespace_):
            checkout_element = child.find(
                "ns1:transactionConfirmResponse", namespace_)
            result["status_code"] = checkout_element.find("RETURN_CODE").text
            result["desc"] = checkout_element.find("DESCRIPTION").text
            result["trans_id"] = checkout_element.find("TRX_ID").text
            result["merchant_trans_id"] = checkout_element.find(
                "MERCHANT_TRANSACTION_ID").text

        return result

    def transaction_status_request(
            self, merchant_id, pass_key, reference_id, msisdn):
        """Send transaction status request"""
        timestamp, password = encrypt_password(merchant_id, pass_key)
        client = Client(self.checkout_wsdl)
        checkout_header = client.factory.create("CheckOutHeader")
        checkout_header.MERCHANT_ID = merchant_id
        checkout_header.PASSWORD = password
        checkout_header.TIMESTAMP = timestamp
        client.set_options(soap_headers=checkout_header)
        result = client.service.transactionStatusQuery(
            MERCHANT_TRANSACTION_ID=self.merchant_transaction_id,
            TRX_ID=msisdn)
        return result

    @staticmethod
    def transaction_status_response(
            response, result_tag="ns1:transactionStatusResponse") -> dict:
        """Process transaction status request"""
        result = {}
        root = ET.fromstring(response)
        namespace_ = {
            "SOAP-ENV": "http://schemas.xmlsoap.org/soap/envelope/",
            "ns1": "tns:ns"}
        for child in root.findall("SOAP-ENV:Body", namespace_):
            checkout_element = child.find(result_tag, namespace_)
            result["status_code"] = checkout_element.find("RETURN_CODE").text
            result["trans_status"] = checkout_element.find("TRX_STATUS").text
            result["mpesa_trans_id"] = checkout_element.find(
                "M-PESA_TRX_ID").text
            result["amount"] = checkout_element.find(
                "AMOUNT").text
            result["msisdn"] = checkout_element.find(
                "MSISDN").text
            result["trans_date"] = checkout_element.find(
                "M-PESA_TRX_DATE").text
            result["desc"] = checkout_element.find("DESCRIPTION").text
            result["trans_id"] = checkout_element.find("TRX_ID").text
            result["merchant_trans_id"] = checkout_element.find(
                "MERCHANT_TRANSACTION_ID").text

        return result

    def callback_response(self, response) -> dict:
        """Get callback response"""
        return self.transaction_status_response(
            response, "ns1:ResultMsg")
