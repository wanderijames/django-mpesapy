import re
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from mpesapy.models import MpesaCtoBill
from mpesapy.models import MpesaCtoBuy


@csrf_exempt
@require_http_methods(["POST"])
def c2b_paybill(request):
    """HTTP interface to be called by the M-Pesa Pay Bill IPN push. Accepts POST only."""

    def _auth(data):
        """Authenticated the given user and password.

        Args:
            data(dict): data from the POST requests.

        Returns:
            (HttpResponse)

        """
        provided_user = data.get('user')
        provided_pass = data.get('pass')
        required_user = getattr(settings, 'MPESA_PAYBILL_USER', "user")
        required_pass = getattr(settings, 'MPESA_PAYBILL_PASS', "pass")
        return provided_user == required_user and provided_pass == required_pass

    data = request.POST
    if _auth(data):
        mct = MpesaCtoBill.create_push(
            ipn_notification_id=data.get('id'),
            notification_source=data.get('orig'),
            notification_destination=data.get('dest'),
            text_message=data.get('text'),
            mpesa_code=data.get('mpesa_code'),
            mpesa_acc=data.get('mpesa_acc'),
            mpesa_msisdn=data.get('mpesa_msisdn'),
            mpesa_trx_date=data.get('mpesa_trx_date'),
            mpesa_trx_time=data.get('mpesa_trx_time'),
            mpesa_amt=data.get('mpesa_amt'),
            mpesa_sender=data.get('mpesa_sender')
        )
        return HttpResponse("OK|Thank you for your payment")
    else:
        return HttpResponse("FAIL|We could not process your account")


@csrf_exempt
@require_http_methods(["POST"])
def c2b_buy_goods(request):
    """HTTP interface to be called by the M-Pesa Buy Goods IPN push. Accepts POST only."""

    def _auth(data):
        """Authenticated the given user and password.

        Args:
            data(dict): data from the POST requests.

        Returns:
            (HttpResponse)

        """
        provided_user = data.get('user')
        provided_pass = data.get('pass')
        required_user = getattr(settings, 'MPESA_BUY_USER', "user")
        required_pass = getattr(settings, 'MPESA_BUY_PASS', "pass")
        return provided_user == required_user and provided_pass == required_pass

    data = request.POST
    if _auth(data):
        try:
            text = data.get('text')
            text = text.replace(",","")
            amounts = re.findall("\d+\.\d+",text)
            mpesa_amt = float(amounts[0])
            person = re.findall(r"from \d+ \w+ \w+",text)
            if len(person) > 0:
                every = person[0].split(" ")
                mpesa_msisdn = every[1]
                mpesa_sender = " ".join(every[2:])
            MpesaCtoBuy.create_push(ipn_notification_id=data.get("id"),
                                            text_message=data.get("text"),
                                            mpesa_code=data.get("mpesa_code"),
                                            mpesa_msisdn=mpesa_msisdn,
                                            mpesa_sender=mpesa_sender,
                                            mpesa_amt=mpesa_amt)
        except:
            MpesaCtoBuy.objects.create(ipn_notification_id=data.get("id"),
                                            text_message=data.get("text"),
                                            mpesa_code=data.get("mpesa_code"))
        return HttpResponse("OK|Thank you for your payment")
    else:
        return HttpResponse("FAIL|We could not process your account")
