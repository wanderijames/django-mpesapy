from datetime import datetime
from base64 import b64encode
import hashlib
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from .utils import kenya_time
from .wsdl import (
    C2B_PAYMENT_CONFIRMATION_RESULT,
    C2B_PAYMENT_VALIDATION_RESULT,
    REGISTER_URL)


class C2B:
    reference_id = None
    result_code = None

    def _find(self, element, tag):
        relement = element.find(tag)
        if isinstance(relement, Element):
            return relement.text
        return ""

    def enc_password(self, identifier, password):
        """Used to construct sp_password used in authentification
        within M-Pesa broker

        :param identifier: Can be SP_ID or MERCHANT_ID issued by M-Pesa broker
        :param password: Password issued by M-Pesa broker for authentification
        purposes
        :type identifier: str
        :type password: str
        :return: A tuple with  timestamp and encrypted password
        :rtype: tuple

        """
        nw = kenya_time()
        time_stamp = nw.strftime("%Y%m%d%H%M%S")
        hashed = hashlib.sha256(
            "{}{}{}".format(
                identifier,
                password,
                time_stamp)).hexdigest()
        return time_stamp, b64encode(hashed)

    def register_url(self, short_code, org_short_name,
                     request_id, validation_url, confirmation_url,
                     sp_id, sp_password, time_stamp, service_id):
        return REGISTER_URL.format(
            short_code=short_code, org_short_name=org_short_name,
            request_id=request_id, validation_url=validation_url,
            confirmation_url=confirmation_url, sp_id=sp_id,
            sp_password=sp_password, time_stamp=time_stamp,
            service_id=service_id)

    def register_url_request(self, in_xml):
        result = {}
        root = ET.fromstring(in_xml)
        ns = {"soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
              "req": "http://api-v1.gen.mm.vodafone.com/mminterface/request"}
        for child in root.findall("soapenv:Body", ns):
            element = child.find("req:ResponseMsg", ns).text
            response_code = re.search("<ResponseCode>.*</ResponseCode>",
                                      element)
            response_desc = re.search("<ResponseDesc>.*</ResponseDesc>",
                                      element)
            service_status = re.search("<ServiceStatus>.*</ServiceStatus>",
                                       element)
            if response_code is not None:
                result["result_code"] = ET.fromstring(
                    response_code.group(0)).text
            if response_desc is not None:
                result["desc"] = ET.fromstring(
                    response_desc.group(0)).text
            if service_status is not None:
                result["service_status"] = ET.fromstring(
                    service_status.group(0)).text
        return result

    def confirmation_result(self, reference_id):
        return C2B_PAYMENT_CONFIRMATION_RESULT.format(
            reference_id=reference_id)

    def validation_result(self, reference_id, result_code=0, result_desc=""):
        return C2B_PAYMENT_VALIDATION_RESULT.format(
            reference_id=reference_id,
            result_desc=result_desc,
            result_code=result_code)

    def validation_request(self, in_xml):
        result = {}
        root = ET.fromstring(in_xml)
        ns = {"soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
              "c2b": "http://cps.huawei.com/cpsinterface/c2bpayment"}
        for child in root.findall("soapenv:Body", ns):
            checkout_element = child.find(
                "c2b:C2BPaymentValidationRequest", ns)
            result["transaction_type"] = self._find(
                checkout_element, "TransType")
            result["trans_id"] = self._find(
                checkout_element, "TransID")
            result["trans_time"] = datetime.strptime(
                checkout_element.find("TransTime").text,
                "%Y%m%d%H%M%S")
            result["amount"] = self._find(
                checkout_element, "TransAmount")
            result["business"] = self._find(
                checkout_element, "BusinessShortCode")
            result["account"] = self._find(
                checkout_element, "BillRefNumber")
            result["amount"] = self._find(
                checkout_element, "TransAmount")
            names = [x.text for x in checkout_element.iter("KYCValue")]
            result["sender"] = " ".join(names).strip()

            result["msisdn"] = self._find(
                checkout_element, "MSISDN")
        return result

    def confirmation_request(self, in_xml):
        result = {}
        root = ET.fromstring(in_xml)
        ns = {"soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
              "c2b": "http://cps.huawei.com/cpsinterface/c2bpayment"}
        for child in root.findall("soapenv:Body", ns):
            checkout_element = child.find(
                "c2b:C2BPaymentConfirmationRequest", ns)
            result["transaction_type"] = self._find(
                checkout_element, "TransType")
            result["trans_id"] = self._find(
                checkout_element, "TransID")
            result["trans_time"] = datetime.strptime(
                checkout_element.find("TransTime").text,
                "%Y%m%d%H%M%S")
            result["tstamp"] = result["trans_time"].strftime(
                "%Y-%m-%d %I:%M:%S")
            result["amount"] = self._find(
                checkout_element, "TransAmount")
            result["business"] = self._find(
                checkout_element, "BusinessShortCode")
            result["account"] = self._find(
                checkout_element, "BillRefNumber")
            result["balance"] = self._find(
                checkout_element, "OrgAccountBalance")
            result["reference_id"] = self._find(
                checkout_element, "ThirdPartyTransID")
            result["amount"] = self._find(
                checkout_element, "TransAmount")
            names = [x.text for x in checkout_element.iter("KYCValue")]
            result["sender"] = " ".join(names).strip()
            result["msisdn"] = self._find(
                checkout_element, "MSISDN")
        return result
