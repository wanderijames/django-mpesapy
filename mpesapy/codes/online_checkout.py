"""Transaction codes for tha app"""
# pylint: disable=line-too-long,invalid-name

CODES = {
    "00": "The Request has been successfully received or the transaction has successfully completed.",
    "01": "Insufficient Funds on MSISDN account",
    "03": "Amount less than the minimum single transfer allowed on the system.",
    "04": "Amount more than the maximum single transfer amount allowed.",
    "05": "Transaction expired in the instance where it wasn’t picked in time for processing.",
    "06": "Transaction could not be confirmed possibly due to confirm operation failure.",
    "08": "Balance would rise above the allowed maximum amount.  This happens if the MSISDN has reached its maximum transaction limit for the day.",  # NOQA
    "09": "The store number specified in the transaction could not be found.  This happens if the Merchant Pay bill number was incorrectly captured during registration.",  # NOQA
    "10": "This occurs when the system is unable to resolve the credit account i.e the MSISDN provided isn’t registered on M-PESA",  # NOQA
    "11": "This message is returned when the system is unable to complete the transaction.",
    "12": "Message returned when if the transaction details are different from original captured request details.",
    "29": "System Downtime message when the system is inaccessible.",
    "30": "Returned when the request is missing reference ID",
    "31": "Returned when the request amount is Invalid or blank",
    "32": "Returned when the account in the request hasn’t been activated.",
    "33": "Returned when the account hasn’t been approved to transact.",
    "34": "Returned when there is a request processing delay. ",
    "35": "Response when a duplicate request is detected.",
    "36": "Response given if incorrect credentials are provided in the request",
    "40": "Missing parameters",
    "41": "MSISDN is in incorrect format"
}
