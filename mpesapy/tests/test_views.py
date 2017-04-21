import random
import logging
import xml.etree.ElementTree as ET
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
import mpesapy.models as mdl
from mpesapy.mpesa import c2b, wsdl
from mpesapy import tasks


class ModelsTestCase(TestCase):
    def setUp(self):
        mdl.Business(
            number="12345",
            name="Company A ltd",
            extra={"MERCHANT_ID": "3e23232",
                   "SERVICE_ID": "3434",
                   "SP_ID": "5454478",
                   "SP_PASS": "SDFGFdfdr",
                   "ipn_endpoint": "https://host",
                   "ipn_user": "user",
                   "ipn_password": "pass",
                   "api_key": "apikeyhere"
                   }).save()

        mdl.Business(
            number="54321",
            name="Company B ltd",
            bnt=mdl.Business.C2B_TILL,
            extra={"MERCHANT_ID": "2323EW",
                   "SERVICE_ID": "SDSS",
                   "SP_ID": "34354",
                   "SP_PASS": "RSDRdfd"
                   }).save()

    def test_register_url_response(self):
        with open(
            "{}/registerURL_kenya_result.xml".format(
                wsdl.WSDL), "r") as xml_file:
            content = xml_file.read()
            c2b_obj = c2b.C2B()
            response = c2b_obj.register_url_request(content)
            self.assertEqual(response.get("result_code"), "00000000")
            self.assertEqual(response.get("desc"), "success")

    def test_register_url_request(self):
        host = "http://"
        biz = mdl.Business.objects.get(number="12345")
        extra = biz.extra_data()
        short_name = extra.get("short_name", biz.short_name())
        business_details = {}
        confirmation_url = "{}{}".format(
            host, reverse(
                "c2b_confirmation",
                kwargs={"business": biz.number}))
        validation_url = "{}{}".format(
            host, reverse(
                "c2b_validate",
                kwargs={"business": biz.number}))
        business_details["number"] = biz.number
        business_details["SP_ID"] = extra.get("SP_ID")
        business_details["SERVICE_ID"] = extra.get("SERVICE_ID")
        business_details["name"] = short_name
        business_details["SP_PASS"] = extra.get("SP_PASS")
        business_details["request_id"] = random.randint(1, 10**5)
        response = tasks.register_url(
            validation_url, confirmation_url,
            business_details, TEST=True)
        logging.info(response)

    def test_c2b_paybill_validation_view(self):
        c = Client()
        with open(
            "{}/C2BPaymentValidationRequest.xml".format(
                wsdl.WSDL), "r") as xml_file:
            content = xml_file.read()
            response = c.post(
                path="/v2/validate/12345/c2b",
                data=content,
                content_type="application/xml")
        self.assertEqual(response.status_code, 200)
        root = ET.fromstring(response.content)
        ns = {"soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
              "c2b": "http://cps.huawei.com/cpsinterface/c2bpayment"}
        for child in root.findall("soapenv:Body", ns):
            checkout_element = child.find("c2b:C2BPaymentValidationResult", ns)
            result = checkout_element.find("ResultCode").text
            self.assertEqual(result is not None, True)

    def test_c2b_paybill_confirmation_view(self):
        c = Client()
        with open(
            "{}/C2BPaymentConfirmationRequest.xml".format(
                wsdl.WSDL), "r") as xml_file:
            content = xml_file.read()
            response = c.post(
                path="/v2/confirm/12345/c2b",
                data=content,
                content_type="application/xml")
        self.assertEqual(response.status_code, 200)
        root = ET.fromstring(response.content)
        ns = {"soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
              "c2b": "http://cps.huawei.com/cpsinterface/c2bpayment"}
        for child in root.findall("soapenv:Body", ns):
            checkout_element = child.find("c2b:C2BPaymentConfirmationResult",
                                          ns)
            self.assertEqual(checkout_element.text.startswith(
                "C2B Payment Transaction"), True)
