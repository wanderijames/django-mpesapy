"""Customer to Business (C2B) logic"""
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
    """Customer to Business helpers"""
    reference_id = None
    result_code = None

    @staticmethod
    def _find(element, tag):
        """Get text from an XML using its tag"""
        relement = element.find(tag)
        if isinstance(relement, Element):
            return relement.text
        return ""

    @staticmethod
    def enc_password(identifier, password):
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
        time_stamp = kenya_time().strftime("%Y%m%d%H%M%S")
        hashed = hashlib.sha256(
            "{}{}{}".format(
                identifier,
                password,
                time_stamp).encode()).hexdigest().encode()
        return time_stamp, b64encode(hashed)

    @staticmethod
    def register_url(short_code, org_short_name,
                     request_id, validation_url, confirmation_url,
                     sp_id, sp_password, time_stamp, service_id):
        """Build url for registering our mpesa endpoint"""
        # pylint: disable=too-many-arguments
        return REGISTER_URL.format(
            short_code=short_code, org_short_name=org_short_name,
            request_id=request_id, validation_url=validation_url,
            confirmation_url=confirmation_url, sp_id=sp_id,
            sp_password=sp_password, time_stamp=time_stamp,
            service_id=service_id)

    @staticmethod
    def register_url_request(in_xml) -> dict:
        """extract data from register-url request response"""
        result = {}
        root = ET.fromstring(in_xml)
        namespace_ = {
            "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
            "req": "http://api-v1.gen.mm.vodafone.com/mminterface/request"
        }
        for child in root.findall("soapenv:Body", namespace_):
            element = child.find("req:ResponseMsg", namespace_).text
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

    @staticmethod
    def confirmation_result(reference_id: str) -> str:
        """confirmation receipt xml"""
        return C2B_PAYMENT_CONFIRMATION_RESULT.format(
            reference_id=reference_id)

    @staticmethod
    def validation_result(
            reference_id: str,
            result_code: int = 0,
            result_desc: str = "") -> str:
        """validation result xml"""
        return C2B_PAYMENT_VALIDATION_RESULT.format(
            reference_id=reference_id,
            result_desc=result_desc,
            result_code=result_code)

    def validation_request(self, in_xml: str) -> dict:
        """Extract data from validation request response"""
        result = {}
        root = ET.fromstring(in_xml)
        namespace_ = {
            "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
            "c2b": "http://cps.huawei.com/cpsinterface/c2bpayment"
        }
        for child in root.findall("soapenv:Body", namespace_):
            checkout_element = child.find(
                "c2b:C2BPaymentValidationRequest", namespace_)
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

    def confirmation_request(self, in_xml: str) -> dict:
        """Extract data from confirmation request response"""
        result = {}
        root = ET.fromstring(in_xml)
        namespace_ = {
            "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
            "c2b": "http://cps.huawei.com/cpsinterface/c2bpayment"
        }
        for child in root.findall("soapenv:Body", namespace_):
            checkout_element = child.find(
                "c2b:C2BPaymentConfirmationRequest", namespace_)
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
