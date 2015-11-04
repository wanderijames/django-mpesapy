import random
import datetime
from django.utils import timezone
from django.db import models
from django.core.signing import Signer


class URLSafeField:
    """Creates URL safe identifiers instead of table column ID nor slug field"""

    @classmethod
    def encrypt(cls, hash):
        """Generates the URL safe identifier from the table column ID and salt

        Args:
            hash(str): stringified table column ID

        Returns:
            str: The URL safe identifier

        Raises:
            AssertError: If the table column ID is not stringified

        """
        assert (type(hash) == str) and len(hash) > 0, "Incorrect hash cannot be encrypted"
        hash = "{}{}".format(hash, random.randint(1, 100))
        sgn = Signer()
        value = sgn.sign(hash)
        return value.split(":")[1]


class FlatModel(models.Model):
    """Defines common fields and function to be used by other models"""
    removed = models.BooleanField(default=False)
    registered_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)
    urlsafe = models.CharField(max_length=256, null=True, blank=True, editable=False)

    @property
    def build_urlsafe(self):
        if self.urlsafe is not None:
            return self.urlsafe
        else:
            cryp = URLSafeField.encrypt(str(self.id))
            self.urlsafe = cryp
            self.save()
            return str(cryp)

    class Meta:
        abstract = True
        app_label = "mpesapy"

    def was_registered_recently(self):
        return self.registered_date >= timezone.now() - datetime.timedelta(days=1)

    def was_updated_recently(self):
        return self.updated_date >= timezone.now() - datetime.timedelta(days=1)

    was_updated_recently.admin_order_field = 'pub_date'
    was_updated_recently.boolean = True
    was_updated_recently.short_description = 'Updated recently?'


class MpesaRecords(FlatModel):
    ipn_notification_id = models.CharField(max_length=20, null=True, blank=True, help_text="Notification ID")
    text_message = models.CharField(max_length=200, null=True, blank=True)
    mpesa_code = models.CharField(max_length=20, unique=True, db_index=True)
    mpesa_amt = models.FloatField(max_length=100, null=True, blank=True)
    mpesa_msisdn = models.CharField(max_length=150, null=True, blank=True)
    mpesa_sender = models.CharField(max_length=200, null=True, blank=True)
    processed = models.BooleanField(default=False)
    date_received = models.DateTimeField(auto_now_add=True)
    date_processed = models.DateTimeField(auto_now=True)
    counter_checked = models.BooleanField(default=False)

    class Meta:
        abstract = True
        app_label = "mpesapy"

    def __unicode__(self):  # Python 3: def __str__(self):
        return unicode("%s" % (self.mpesa_code))

    @classmethod
    def retrieve(cls, mpesa_code):
        return cls.objects.filter(mpesa_code=mpesa_code)

    @classmethod
    def exists(cls, mpesa_code):
        return len(cls.retrieve(mpesa_code)) > 0

    @classmethod
    def create_pull(cls, **kwargs):
        if cls.exists(kwargs.get('mpesa_code')):
            return cls.retrieve(kwargs.get('mpesa_code'))[0]
        else:
            entity = cls(**kwargs).save()
            entity.counter_checked = True
            return entity.save()


class MpesaCtoBill(MpesaRecords):
    """Table that holds M-Pesa paybill messages"""

    notification_source = models.CharField(max_length=100, null=True, blank=True, help_text="Notification source")
    notification_destination = models.CharField(max_length=100, null=True, blank=True,
                                                help_text="Notification destination")
    mpesa_acc = models.CharField(db_index=True, max_length=200)
    mpesa_trx_date = models.CharField(max_length=100)
    mpesa_trx_time = models.CharField(max_length=100)

    class Meta:
        verbose_name = "M-Pesa C2B"
        verbose_name_plural = "M-Pesa C2Bs"
        app_label = "mpesapy"

    def save(self, *args, **kwargs):
        if self._state.adding:
            chk = MpesaCtoBill.retrieve(mpesa_code=self.mpesa_code)
            if len(chk) > 0:
                return chk[0]
            self.mpesa_amt = float(self.mpesa_amt)
            super(MpesaCtoBill, self).save(*args, **kwargs)
            return self
        super(MpesaCtoBill, self).save(*args, **kwargs)
        return self

    @classmethod
    def create_push(cls, **kwargs):
        if cls.exists(kwargs.get('mpesa_code')):
            entity = cls.retrieve(kwargs.get('mpesa_code'))[0]
            if not entity.ipn_notification_id:
                entity.ipn_notification_id = kwargs['ipn_notification_id']
                entity.notification_source = kwargs['notification_source']
                entity.notification_destination = kwargs['notification_destination']
                entity.notification_time_received = kwargs['notification_time_received']
                entity.text_message = kwargs['text_message']
                entity.mpesa_trx_date = kwargs['mpesa_trx_date']
                entity.mpesa_trx_time = kwargs['mpesa_trx_time']
                entity.counter_checked = True
                entity.save()
            return entity
        else:
            return cls(**kwargs).save()


class MpesaCtoBuy(MpesaRecords):

    class Meta:
        verbose_name = "M-Pesa C2Buy"
        verbose_name_plural = "M-Pesa C2Buys"
        app_label = "mpesapy"

    def save(self, *args, **kwargs):
        if self._state.adding:
            chk = MpesaCtoBuy.objects.filter(mpesa_code=self.mpesa_code)
            if len(chk) > 0:
                return chk[0]
            self.mpesa_amt = float(self.mpesa_amt)
            super(MpesaCtoBuy, self).save(*args, **kwargs)
            return self
        super(MpesaCtoBuy, self).save(*args, **kwargs)
        return self

    @classmethod
    def create_push(cls, **kwargs):
        if cls.exists(kwargs.get('mpesa_code')):
            entity = cls.retrieve(kwargs.get('mpesa_code'))[0]
            if not entity.ipn_notification_id:
                entity.ipn_notification_id = kwargs['ipn_notification_id']
                entity.text_message = kwargs['text_message']
                entity.counter_checked = True
                entity.save()
            return entity
        else:
            return cls(**kwargs).save()
