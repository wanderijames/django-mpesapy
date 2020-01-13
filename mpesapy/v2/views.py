"""Views for the sub app"""
# pylint: disable=broad-except,unused-argument
# pylint: disable=no-member,inconsistent-return-statements,
import logging
from django.http import HttpResponse
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import mpesapy.models as mdl
from mpesapy.mpesa import c2b as cb
from mpesapy import tasks

# Get an instance of a logger
LOGGER = logging.getLogger(__name__)


def response(data):
    """Build response"""
    return HttpResponse(data, content_type="text/xml")


def authenticate(url_biz, xml_biz, user=None, password=None):
    """Checks credentials validity of a business

    :param url_biz: M-PESA business number in the URL
    :param xml_biz: M-PESA business number in request body
    :param user: Username set by the business for M-Pesa use
    :param password: Password set by the business for M-Pesa use
    :type url_biz: str
    :type xml_biz: str
    :type user: str
    :type password: str
    :return: Business if check passed otherwise None
    :rtype: Business

    """
    try:
        business = mdl.Business.objects.get(number=str(url_biz))
        extra_data = business.extra_data()
        if user and password:
            buser = extra_data.get("user", user)
            bpass = extra_data.get("pass", password)
            if buser == user and bpass == password:
                return business
        if str(url_biz) != str(xml_biz):
            if xml_biz not in extra_data.get(
                    "numbers", "").split(","):
                return
        return business
    except mdl.Business.DoesNotExist:
        print("does not exist")


@csrf_exempt
@require_http_methods(["POST"])
def c2b_validation(request, *args, **kwargs):
    """Endpoint to be consumed by M-Pesa validation request.

    Accepts HTTP POST oherwise a 403 will occur.
    Accepts content_type='application/xml'

    Expects 'business' in kwargs.

    """
    body = request.body.decode()
    tasks.log_request.delay(request.path, body)
    c2b = cb.C2B()
    try:
        data = c2b.validation_request(body)
    except Exception as err:
        LOGGER.exception(str(err))
        LOGGER.info(body)
        return response(
            c2b.validation_result(
                "C2B00016", "C2B00016", "Unknown error occurred"))
    ref = "0000"
    result_code = "C2B00016"
    biz = authenticate(
        kwargs.get("business"),
        data.get("business"),
        data.get("user", None),
        data.get("pass", None))
    result_desc = "Business number not found"
    if biz is not None:
        copy_data = data.copy()
        del copy_data["trans_time"]
        if "user" in data:
            del copy_data["user"]
        if "pass" in data:
            del copy_data["pass"]
        log = mdl.APILog.create(
            data.get("business"),
            extra=copy_data)
        ref = log.ref
        result_code = 0
        result_desc = ""
    return response(
        c2b.validation_result(
            ref, result_code=result_code, result_desc=result_desc))


@csrf_exempt
@require_http_methods(["POST"])
def c2b_confirmation(request, *args, **kwargs):
    """Endpoint to be consumed by M-Pesa confirmation request.

    Accepts HTTP POST otherwise a 403 will occur.
    Accepts content_type='application/xml'

    Expects 'business' in kwargs.

    """
    body = request.body.decode()
    tasks.log_request.delay(request.path, body)
    c2b = cb.C2B()
    try:
        data = c2b.confirmation_request(body)
    except Exception as err:
        LOGGER.exception(str(err))
        LOGGER.info(body)
        return response(
            c2b.confirmation_result("000000"))
    biz = authenticate(
        kwargs.get("business"),
        data.get("business"),
        data.get("user", None),
        data.get("pass", None))
    result_code = "C2B00014"
    if biz is not None:
        try:
            rec = mdl.MpesaBase(
                business=biz,
                code=data.get("trans_id"),
                amount=float(data.get("amount")),
                msisdn=data.get("msisdn"),
                person=data.get("sender"),
                extra={
                    "balance": data.get("balance"),
                    "account": data.get("account"),
                    "transaction_type": data.get("transaction_type"),
                    "reference_id": data.get("reference_id", "")}
            ).save(created=data.get("trans_time"))
            result_code = rec.code
            tasks.ipn.apply_async(
                (data, biz.extra_data()),
                task_id=data["trans_id"],
                max_retries=3, soft_time_limit=30,
                time_limit=90, countdown=1
            )
        except IntegrityError:
            pass
    return HttpResponse(
        c2b.confirmation_result(result_code))
