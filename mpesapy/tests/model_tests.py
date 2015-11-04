import random
from django.test import TestCase
from mpesapy.models import MpesaCtoBill


class MpesaCtoBillTestCase(TestCase):
    def setUp(self):
        orig = "MPESA"
        dest = "254700456584"
        user = "user"
        passw = "password"
        mpesa_msisdn = "2547200000000"
        mpesa_trx_date = "24/3/15"
        mpesa_trx_time = "2:36 PM"
        mpesa_sender = "ANTHONY JOE"
        business_number = "000000"
        cum = 0
        text = "{transaction_code} Confirmed. on 24/3/15 at 2:36 PM Ksh{amount}.00 received from JOE DOE " \
               "2547200000000. Account Number 4545 New Utility balance is Ksh{cumulative_amount}"
        for i in xrange(1000):
            if self._auth(user, passw):
                id = str(i)
                mpesa_code = "test" + id
                mpesa_amt = 50 * i
                cum += mpesa_amt
                text = text.format(transaction_code=mpesa_code, amount=mpesa_amt, cumulative_amount=cum)
                MpesaCtoBill.create_push(ipn_notification_id=id, text_message=text, mpesa_code=mpesa_code,
                                         mpesa_amt=mpesa_amt, mpesa_msisdn=mpesa_msisdn,
                                         mpesa_sender=mpesa_sender, notification_source=orig,
                                         notification_destination=dest, mpesa_acc=business_number,
                                         mpesa_trx_date=mpesa_trx_date, mpesa_trx_time=mpesa_trx_time)

    def _auth(self, user, passw):
        required_user = "user"
        required_pass = "password"
        return user == required_user and passw == required_pass

    def test_record_keeping(self):
        """Check records that have been saved and their existence"""
        all_entities = MpesaCtoBill.objects.all()
        self.assertEqual(1000, len(all_entities))
        self.assertEqual(True, MpesaCtoBill.exists("test1"))
        self.assertEqual(False, MpesaCtoBill.exists("tesst1"))
