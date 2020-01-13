"""Signals for the app"""
import logging
import random
from django.urls import reverse
from django.conf import settings
import mpesapy.tasks as tsk


def register_callback(sender, instance, **kwargs):
    """Callback for registering URL on the M-Pesa platform

    **kwargs is Used to send any param=value pairs

    :param sender: The Model being affected
    :param instance: The model instance being affected
    :type sender: Business
    :type instance: Business()
    :return: async task that does the actual job
    :rtype: tsk.register_url_task

    """
    logging.info(str(sender))
    if not instance.registered and instance.register:
        host = getattr(settings, "MPESA_HOST_KEY", "http://")
        biz = instance
        extra = biz.extra_data().copy()
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
        business_details["request_id"] = kwargs.get(
            "request_id", random.randint(1, 10**5))
        response = tsk.register_url.delay(
            validation_url, confirmation_url,
            business_details,
            TEST=getattr(settings, "TEST", False))
        return response
    return None
