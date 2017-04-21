from datetime import datetime, timedelta
from django.test import TestCase
import mpesapy.models as mdl


class ModelsTestCase(TestCase):
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
        text = "{transaction_code} Confirmed. on 24/3/15 at 2:36 PM "\
            "Ksh{amount}.00 received from JOE DOE " \
            "2547200000000. Account Number 4545 New "\
            "Utility balance is Ksh{cumulative_amount}"
        for i in xrange(1000):
            if self._auth(user, passw):
                id = str(i)
                mpesa_code = "test" + id
                mpesa_amt = 50 * i
                cum += mpesa_amt
                text = text.format(
                    transaction_code=mpesa_code,
                    amount=mpesa_amt, cumulative_amount=cum)
                mdl.MpesaCtoBill.create_push(
                    ipn_notification_id=id, text_message=text,
                    mpesa_code=mpesa_code, mpesa_amt=mpesa_amt,
                    mpesa_msisdn=mpesa_msisdn, mpesa_sender=mpesa_sender,
                    notification_source=orig, notification_destination=dest,
                    mpesa_acc=business_number, mpesa_trx_date=mpesa_trx_date,
                    mpesa_trx_time=mpesa_trx_time)
        mdl.Business(
            number="12345",
            name="Company A ltd",
            extra={"MERCHANT_ID": "3e23232",
                   "SERVICE_ID": "3434",
                   "user": "user",
                   "pass": "password",
                   "SP_ID": "232442",
                   "SP_PASS": "3DS3EW%"}).save()

        mdl.Business(
            number="54321",
            name="Company B ltd",
            bnt=mdl.Business.C2B_TILL,
            extra={"MERCHANT_ID": "2323EW",
                   "SERVICE_ID": "SDSS",
                   "user": "user2",
                   "pass": "password2",
                   "SP_ID": "343645",
                   "SP_PASS": "4RCYVES"}).save()

    def _auth(self, user, passw):
        required_user = "user"
        required_pass = "password"
        return user == required_user and passw == required_pass

    def test_mpesa_api_logs(self):
        log = mdl.APILog.create(
            business_number="600600",
            extra={"trans_id": "sdseewe",
                   "amount": 1000.00}
        )
        self.assertEqual(isinstance(log, mdl.APILog), True)
        self.assertEqual(log.ref is not None, True)
        self.assertEqual("trans_id:sdseewe" in str(log.extra), True)
        self.assertEqual("amount:1000.0" in str(log.extra), True)

    def test_mpesa_base(self):
        nw = datetime.now() - timedelta(minutes=360)
        business = mdl.Business.objects.get(number="12345")
        mb = mdl.MpesaBase(
            business=business,
            code="2323232ed",
            amount=1000.00,
            msisdn="254719000000",
            person="John Doe",
            extra={"account": "3434"}
        ).save(created=nw)
        self.assertEqual(mb.created, nw)
        self.assertEqual(str(mb.code), "2323232ed")

    def test_record_keeping(self):
        """Check records that have been saved and their existence

        """
        all_entities = mdl.MpesaCtoBill.objects.all()
        self.assertEqual(1000, len(all_entities))
        self.assertEqual(True, mdl.MpesaCtoBill.exists("test1"))
        self.assertEqual(False, mdl.MpesaCtoBill.exists("tesst1"))
