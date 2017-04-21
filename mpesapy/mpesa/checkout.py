import xml.etree.ElementTree as ET
from mpesapy.suds.client import Client
from .utils import encrypt_password


class OnlineCheckout(object):

    merchant_transaction_id = None
    reference_id = None
    amount = 0.0
    enc_params = None
    callback_url = None
    callback_method = "xml"
    checkout_wsdl = "https://www.safaricom.co.ke/mpesa_online/lnmo_checkout_server.php?wsdl"

    def __init__(self, *args, **kwargs):
        for k in kwargs:
            setter = getattr(self, "set_{}".format(k), None)
            if setter is not None:
                setter(kwargs[k])

    def set_merchant_transaction_id(self, id):
        self.merchant_transaction_id = id

    def set_reference_id(self, id):
        self.reference_id = id

    def set_amount(self, amount):
        self.amount = amount

    def set_enc_params(self, enc_params):
        self.enc_params = enc_params

    def set_callback_url(self, callback_url):
        self.callback_url = callback_url

    def set_callback_method(self, callback_method):
        self.callback_method = callback_method

    def process_checkout_request(self, merchant_id, pass_key,
                                 msisdn):
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

    def process_checkout_response(self, response):
        result = {}
        root = ET.fromstring(response)
        ns = {"SOAP-ENV": "http://schemas.xmlsoap.org/soap/envelope/",
              "ns1": "tns:ns"}
        for child in root.findall("SOAP-ENV:Body", ns):
            checkout_element = child.find("ns1:processCheckOutResponse", ns)
            result["status_code"] = checkout_element.find("RETURN_CODE").text
            result["desc"] = checkout_element.find("DESCRIPTION").text
            result["trans_id"] = checkout_element.find("TRX_ID").text
            result["message"] = checkout_element.find("CUST_MSG").text

        return result

    def confirm_transaction_request(self, merchant_id, pass_key, reference_id,
                                    msisdn):
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

    def confirm_transaction_response(self, response):
        result = {}
        root = ET.fromstring(response)
        ns = {"SOAP-ENV": "http://schemas.xmlsoap.org/soap/envelope/",
              "ns1": "tns:ns"}
        for child in root.findall("SOAP-ENV:Body", ns):
            checkout_element = child.find("ns1:transactionConfirmResponse", ns)
            result["status_code"] = checkout_element.find("RETURN_CODE").text
            result["desc"] = checkout_element.find("DESCRIPTION").text
            result["trans_id"] = checkout_element.find("TRX_ID").text
            result["merchant_trans_id"] = checkout_element.find(
                "MERCHANT_TRANSACTION_ID").text

        return result

    def transaction_status_request(self, merchant_id, pass_key, reference_id,
                                   msisdn):
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

    def transaction_status_response(self, response,
                                    result_tag="ns1:transactionStatusResponse"):
        result = {}
        root = ET.fromstring(response)
        ns = {"SOAP-ENV": "http://schemas.xmlsoap.org/soap/envelope/",
              "ns1": "tns:ns"}
        for child in root.findall("SOAP-ENV:Body", ns):
            checkout_element = child.find(result_tag, ns)
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

    def callback_response(self, response):
        return self.transaction_status_response(response,
                                                "ns1:ResultMsg")
