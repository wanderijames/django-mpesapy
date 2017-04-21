import hashlib
import base64
import datetime
import xml.etree.ElementTree as ET
from suds.client import Client

CHECKOUT_URL = "https://safaricom.co.ke/mpesa_online/lnmo_checkout_server.php?wsdl"
MERCHANT_ID = "1234"
PASSKEY = "1213"  # passkey provided by SAG
MERCHANT_TRANSACTION_ID = "12"
REFERENCE = "REF12"


def encrypt_password(merchant_id, passkey):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    hash = hashlib.sha256("{} {} {}".format(
                                            merchant_id,
                                            passkey,
                                            timestamp)).upper()
    return timestamp, base64.b64encode(hash)



# client = Client(CHECKOUT_URL)
# timestamp, password = encrypt_password(MERCHANT_ID, PASSKEY)
# checkout_header = client.factory.create("CheckOutHeader")
# checkout_header.MERCHANT_ID = "1244324"
# checkout_header.PASSWORD = password
# checkout_header.TIMESTAMP = timestamp
# client.set_options(soap_headers=checkout_header)
# result = client.service.processCheckOut(
#                                         MERCHANT_TRANSACTION_ID="",
#                                         REFERENCE="",
#                                         AMOUNT="",
#                                         MSISDN="",
#                                         )

# xml = """
# <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="tns:ns">
#    <SOAP-ENV:Body>
#       <ns1:processCheckOutResponse>
#          <RETURN_CODE>00</RETURN_CODE>
#          <DESCRIPTION>Success</DESCRIPTION>
#          <TRX_ID>cce3d32e0159c1e62a9ec45b67676200</TRX_ID>
#          <ENC_PARAMS/>
#          <CUST_MSG>To complete this transaction, enter your Bonga PIN on your handset. if you don't have one dial *126*5# for instructions</CUST_MSG>
#       </ns1:processCheckOutResponse>
#    </SOAP-ENV:Body>
# </SOAP-ENV:Envelope>"""
# result = {}
# root = ET.fromstring(xml)
# ns = {"SOAP-ENV": "http://schemas.xmlsoap.org/soap/envelope/", "ns1": "tns:ns"}
# for child in root.findall("SOAP-ENV:Body", ns):
#     checkout_element = child.find("ns1:processCheckOutResponse", ns)
#     result["status_code"] = checkout_element.find("RETURN_CODE").text
#     result["desc"] = checkout_element.find("DESCRIPTION").text
#     result["trans_id"] = checkout_element.find("TRX_ID").text
#     result["message"] = checkout_element.find("CUST_MSG").text
