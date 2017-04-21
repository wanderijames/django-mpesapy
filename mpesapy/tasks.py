from __future__ import absolute_import

from celery import shared_task
from mpesapy.fetch import URLFetch
from mpesapy.mpesa import c2b
from mpesapi.celery import app


@shared_task
def register_url(validation_url, confirmation_url, business_details, **kwargs):
    """Use this to register URL on M-Pesa broker

    **kwargs is expected to have M-Pesa URL that will be fetched
    by this function

    :param validation_url: URL to register for validation request
    :param confirmation_url: URL to register for confirmation request
    :param business_details: Has business details used for registration
    :type validation_url: str
    :type confirmation_url: str
    :type business_details: dict
    :return: A json data indictating the result of the function
    :rtype: dict

    """
    header = {'Content-Type': 'application/xml'}
    mpesa_url = kwargs.get(
        "mpesa_url",
        "http://portal.safaricom.com/registerURL")
    c2b_obj = c2b.C2B()
    sp_id = business_details.get("SP_ID")
    time_stamp, sp_password = c2b_obj.enc_password(
        sp_id,
        business_details.get("SP_PASS"))

    xml_data = c2b_obj.register_url(
        short_code=business_details.get("number"),
        org_short_name=business_details.get("name"),
        request_id=business_details.get("request_id"),
        validation_url=validation_url,
        confirmation_url=confirmation_url,
        sp_id=business_details.get("SP_ID"),
        sp_password=sp_password,
        time_stamp=time_stamp,
        service_id=business_details.get("SERVICE_ID"))
    if "TEST" in kwargs:
        return xml_data

    fetch = URLFetch(
        mpesa_url, header=header, data=xml_data)
    return c2b_obj.register_url_request(fetch.retrieve())


@app.task(bind=True, max_retries=3, soft_time_limit=30,
          time_limit=90, countdown=1)
def ipn(self, mpesa_details, business_details):
    """Use this to notify another service

    IPN - Instant Payment Notification

    After saving a confirmed M-Pesa transaction, another service/endpoint
    can be notified using this task.

    :param mpesa_details: Has payment details
    :param business_details: Has business details that is required
    for API integration details
    :type mpesa_details: dict
    :type business_details: dict
    :return: HTTP response in JSON, str or XML

    """
    assert isinstance(mpesa_details, dict), "mpesa_details: must be dict"
    assert isinstance(business_details, dict), "business_details: must be dict"
    endpoint = business_details.get("ipn_endpoint", "")
    if not endpoint:
        return "No ipn_endpoint"
    user = business_details.get("ipn_user")
    password = business_details.get("ipn_pass")
    apikey = business_details.get("api_key")

    if "user" in business_details:
        del business_details["user"]

    if "pass" in business_details:
        del business_details["pass"]

    data = {
        "ipnuser": user,
        "ipnpass": password,
        "ipnkey": apikey}
    data.update(mpesa_details)
    fetch = URLFetch(endpoint, data=data, return_type="text/plain")
    return fetch.retrieve()


@shared_task
def register_url_task(*args, **kwargs):
    return register_url(*args, **kwargs)


@shared_task
def log_request(path, body, *args, **kwargs):
    import mpesapy.models as mdl
    log = mdl.RequestLogs(path=path, body=body).save()
    return log.id
