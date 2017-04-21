import os

WSDL = os.path.dirname(os.path.abspath(__file__))

C2B_PAYMENT_CONFIRMATION_RESULT = """
<soapenv:Envelope
	xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
	xmlns:c2b="http://cps.huawei.com/cpsinterface/c2bpayment">
	<soapenv:Header/>
	<soapenv:Body>
		<c2b:C2BPaymentConfirmationResult>C2B Payment Transaction {reference_id} result received.</c2b:C2BPaymentConfirmationResult>
	</soapenv:Body>
</soapenv:Envelope>
"""

C2B_PAYMENT_VALIDATION_RESULT = """
<soapenv:Envelope
	xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
	xmlns:c2b="http://cps.huawei.com/cpsinterface/c2bpayment">
	<soapenv:Header/>
	<soapenv:Body>
		<c2b:C2BPaymentValidationResult>
			<ResultCode>{result_code}</ResultCode>
			<ResultDesc>{result_desc}</ResultDesc>
			<ThirdPartyTransID>{reference_id}</ThirdPartyTransID>
		</c2b:C2BPaymentValidationResult>
	</soapenv:Body>
</soapenv:Envelope>
"""

REGISTER_URL = """
<soapenv:Envelope
	xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
	xmlns:req="http://api-v1.gen.mm.vodafone.com/mminterface/request">
	<soapenv:Header>
		<tns:RequestSOAPHeader
			xmlns:tns="http://www.huawei.com/schema/osg/common/v2_1">
			<tns:spId>{sp_id}</tns:spId>
			<tns:spPassword>{sp_password}</tns:spPassword>
			<tns:timeStamp>{time_stamp}</tns:timeStamp>
			<tns:serviceId>{service_id}</tns:serviceId>
		</tns:RequestSOAPHeader>
	</soapenv:Header>
	<soapenv:Body>
		<req:RequestMsg>
			<![CDATA[
			<?xml version="1.0" encoding="UTF-8"?><request
			xmlns="http://api-v1.gen.mm.vodafone.com/mminterface/request"><Transaction><CommandID>RegisterURL</CommandID><OriginatorConversationID>{short_code}_{org_short_name}_{request_id}</OriginatorConversationID><Parameters><Parameter><Key>ResponseType</Key><Value>Completed</Value></Parameter></Parameters><ReferenceData><ReferenceItem><Key>ValidationURL</Key><Value>{validation_url}</Value></ReferenceItem><ReferenceItem><Key>ConfirmationURL</Key><Value>{confirmation_url}</Value></ReferenceItem></ReferenceData></Transaction><Identity><Caller><CallerType>0</CallerType><ThirdPartyID/><Password/><CheckSum/><ResultURL/></Caller><Initiator><IdentifierType>1</IdentifierType><Identifier/><SecurityCredential/><ShortCode/></Initiator><PrimaryParty><IdentifierType>1</IdentifierType><Identifier/><ShortCode>{short_code}</ShortCode></PrimaryParty></Identity><KeyOwner>1</KeyOwner></request>]]>
		</req:RequestMsg>
	</soapenv:Body>
</soapenv:Envelope>
"""

TEST = """
<soapenv:Envelope
	xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
	xmlns:c2b="http://cps.huawei.com/cpsinterface/c2bpayment">
	<soapenv:Header/>
	<soapenv:Body>
		<c2b:C2BPaymentConfirmationRequest>
			<TransactionType>PayBill</TransactionType>
			<TransID>1234560000007031</TransID>
			<TransTime>20140227082020</TransTime>
			<TransAmount>123.00</TransAmount>
			<BusinessShortCode>12345</BusinessShortCode>
			<BillRefNumber>TX1001</BillRefNumber>
			<InvoiceNumber></InvoiceNumber>
			<OrgAccountBalance>12345.00</OrgAccountBalance>
			<ThirdPartyTransID></ThirdPartyTransID>
			<MSISDN>254722703614</MSISDN>
			<KYCInfo>
				<KYCName>[Personal Details][First Name]</KYCName>
				<KYCValue>Hoiyor</KYCValue>
			</KYCInfo>
			<KYCInfo>
				<KYCName>[Personal Details][Middle Name]</KYCName>
				<KYCValue>G</KYCValue>
			</KYCInfo>
			<KYCInfo>
				<KYCName>[Personal Details][Last Name]</KYCName>
				<KYCValue>Chen</KYCValue>
			</KYCInfo>
		</c2b:C2BPaymentConfirmationRequest>
	</soapenv:Body>
</soapenv:Envelope>
"""
