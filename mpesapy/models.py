"""App models"""
# pylint: disable=no-member, arguments-differ
# pylint: disable=too-few-public-methods

import random
import datetime
from django.utils import timezone
from django.db import models
from django.core.signing import Signer
from django.db.models.signals import post_save
from mpesapy.mpesa import (utils, conversion)
import mpesapy.signals as sgn


class BusinessNumberTypesChoices(models.TextChoices):
    """Mpesa transaction types"""
    B2C = 'B2C', 'B2C'
    B2B = 'B2B', 'B2B'
    C2B_BILL = 'C2BB', 'C2B Paybill'
    C2B_TILL = 'C2BT', 'C2B Till'
    C2B_CHECKOUT = 'C2BC', 'C2B Checkout'


class StatusChoices(models.TextChoices):
    """Transaction status"""
    CONSUMED = 'CONS', 'Consumed'
    DECLINED = 'HELD', 'Declined'
    HELD = 'DECL', 'Held'
    REJECTED = 'REJE', 'Rejected'


class URLSafeField:
    """Creates URL safe identifiers

    """

    @classmethod
    def encrypt(cls, row_id: str) -> str:
        """Generates the URL safe identifier from the table row ID and salt

        Args:
            row_id(str): stringified table column ID

        Returns:
            str: The URL safe identifier

        Raises:
            AssertError: If the table column ID is not stringified

        """
        assert isinstance(row_id, str) and row_id, \
            "Incorrect hash cannot be encrypted"
        hashed_row_id = "{}{}".format(row_id, random.randint(1, 100))
        signer = Signer()
        value = signer.sign(hashed_row_id)
        return value.split(":")[1]


class FlatModel(models.Model):
    """Defines common fields and function to be used by other models"""
    removed = models.BooleanField(default=False)
    registered_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=False)
    urlsafe = models.CharField(max_length=256, null=True, blank=True,
                               editable=False)

    @property
    def build_urlsafe(self):
        """Generate urlsafe hash for the row id"""
        if self.urlsafe is not None:
            return self.urlsafe

        cryp = URLSafeField.encrypt(str(self.id))
        self.urlsafe = cryp
        self.save()
        return str(cryp)

    class Meta:
        """Making the parent class an abstract model"""
        abstract = True
        app_label = "mpesapy"

    def was_registered_recently(self):
        """Check latest entity"""
        return self.registered_date >= timezone.now() - datetime.timedelta(
            days=1)

    def was_updated_recently(self):
        """Check latest entity"""
        return self.updated_date >= timezone.now() - datetime.timedelta(days=1)

    was_updated_recently.admin_order_field = 'pub_date'
    was_updated_recently.boolean = True
    was_updated_recently.short_description = 'Updated recently?'


class MpesaRecords(FlatModel):
    """Store mpesa records"""
    ipn_notification_id = models.CharField(
        max_length=20, null=True, blank=True, help_text="Notification ID")
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
        """Making the parent class an abstract model"""
        abstract = True
        app_label = "mpesapy"

    def save(self, *args, **kwargs):
        """Save logic for different scenarios"""
        if self._state.adding:
            chk = self.__class__.retrieve(mpesa_code=self.mpesa_code)
            try:
                return chk[0]
            except IndexError:
                pass
            self.mpesa_amt = float(self.mpesa_amt)
            super().save(*args, **kwargs)
            return self

        super().save(*args, **kwargs)
        return self

    @classmethod
    def retrieve(cls, mpesa_code):
        """Get entities with the code"""
        return cls.objects.filter(mpesa_code=mpesa_code)

    @classmethod
    def exists(cls, mpesa_code):
        """Check if an mpesa transaction exists"""
        return len(cls.retrieve(mpesa_code)) > 0

    @classmethod
    def create_pull(cls, **kwargs):
        """Retrieves records for a certain trsansaction"""
        if cls.exists(kwargs.get('mpesa_code')):
            return cls.retrieve(kwargs.get('mpesa_code'))[0]

        entity = cls(**kwargs).save()
        entity.counter_checked = True
        return entity.save()


class MpesaCtoBill(MpesaRecords):
    """Table that holds M-Pesa paybill messages"""

    notification_source = models.CharField(max_length=100, null=True,
                                           blank=True,
                                           help_text="Notification source")
    notification_destination = models.CharField(
        max_length=100, null=True, blank=True,
        help_text="Notification destination")
    mpesa_acc = models.CharField(db_index=True, max_length=200)
    mpesa_trx_date = models.CharField(max_length=100)
    mpesa_trx_time = models.CharField(max_length=100)

    class Meta:
        """Change the entity names in the admin"""
        verbose_name = "M-Pesa C2B"
        verbose_name_plural = "M-Pesa C2Bs"
        app_label = "mpesapy"

    @classmethod
    def create_push(cls, **kwargs):
        """Create an instant notification"""
        if cls.exists(kwargs.get('mpesa_code')):
            entity = cls.retrieve(kwargs.get('mpesa_code'))[0]
            if not entity.ipn_notification_id:
                entity.ipn_notification_id = kwargs['ipn_notification_id']
                entity.notification_source = kwargs['notification_source']
                entity.notification_destination = kwargs[
                    'notification_destination']
                entity.notification_time_received = kwargs[
                    'notification_time_received']
                entity.text_message = kwargs['text_message']
                entity.mpesa_trx_date = kwargs['mpesa_trx_date']
                entity.mpesa_trx_time = kwargs['mpesa_trx_time']
                entity.counter_checked = True
                entity.save()
            return entity

        return cls(**kwargs).save()


class MpesaCtoBuy(MpesaRecords):
    """Model for customers using c2b buy goods"""

    class Meta:
        """CHanging the name of then entities in admin"""
        verbose_name = "M-Pesa C2Buy"
        verbose_name_plural = "M-Pesa C2Buys"
        app_label = "mpesapy"

    @classmethod
    def create_push(cls, **kwargs):
        """IPN for the entries"""
        if cls.exists(kwargs.get('mpesa_code')):
            entity = cls.retrieve(kwargs.get('mpesa_code'))[0]
            if not entity.ipn_notification_id:
                entity.ipn_notification_id = kwargs['ipn_notification_id']
                entity.text_message = kwargs['text_message']
                entity.counter_checked = True
                entity.save()
            return entity

        return cls(**kwargs).save()


class RequestLogs(models.Model):
    """Model for http requests by mpesa"""
    path = models.CharField(max_length=100, help_text="Request path")
    body = models.TextField(help_text="Request body")
    created = models.DateTimeField(null=True, blank=True, editable=False)
    updated = models.DateTimeField(null=True, blank=True, editable=False)

    def __str__(self):
        return "{}".format(self.path)

    def save(self, *args, **kwargs):
        """To return the saved entity"""
        super(RequestLogs, self).save(*args, **kwargs)
        return self


class Business(models.Model):
    """Store business entity"""

    number = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    bnt = models.CharField(max_length=5, db_index=True,
                           choices=BusinessNumberTypesChoices.choices,
                           default=BusinessNumberTypesChoices.C2B_BILL,
                           help_text="Business number type")
    extra = models.TextField(null=True, blank=True, help_text="important data")
    registered = models.BooleanField(
        default=False,
        help_text="Is URL registered")
    register = models.BooleanField(default=False, help_text="Register URL")
    created = models.DateTimeField(null=True, blank=True, editable=False)
    updated = models.DateTimeField(null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        """Save with custom logic to initate callback registration"""
        self.updated = utils.kenya_time()
        if isinstance(self.extra, dict):
            self.extra = utils.from_json(self.extra)
        if self._state.adding:
            self.created = self.updated
        super(Business, self).save(*args, **kwargs)
        post_save.connect(
            sgn.register_callback,
            dispatch_uid=self.dispatch_uid(),
            sender=self.__class__)
        return self

    def __str__(self):
        return "{}".format(self.number)

    def extra_data(self) -> dict:
        """Return extra column of the entity as json"""
        return utils.to_json(self.extra)

    def short_name(self) -> str:
        """Generate short name"""
        names = self.name.strip().split()
        return "".join([x[:1] for x in names])

    def dispatch_uid(self) -> str:
        """Generate id"""
        return "{}{}{}".format(
            self.__class__.__name__,
            self.id,
            random.randint(1, 10**5))

    def was_registered_recently(self):
        """Check latest entity"""
        return self.created >= utils.kenya_time() - datetime.timedelta(days=1)

    def was_updated_recently(self):
        """Check latest entity"""
        return self.updated >= utils.kenya_time() - datetime.timedelta(days=1)


class MpesaBase(models.Model):
    """Record the transactions"""

    business = models.ForeignKey(
        Business, related_name="mpesabase_business", on_delete=models.PROTECT)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    amount = models.FloatField(max_length=100, null=True, blank=True)
    msisdn = models.CharField(max_length=150, null=True, blank=True)
    person = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=5, db_index=True,
                              choices=StatusChoices.choices,
                              default=StatusChoices.HELD)
    extra = models.TextField(null=True, blank=True, help_text="important data")
    created = models.DateTimeField(null=True, blank=True, editable=False)
    updated = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        """Associate the model to the app"""
        app_label = "mpesapy"

    def save(self, *args, **kwargs):
        """Save logic"""
        self.updated = utils.kenya_time()
        if isinstance(self.extra, dict):
            self.extra = utils.from_json(self.extra)
        if self._state.adding:
            if kwargs.get("created"):
                self.created = kwargs.get("created")
            else:
                self.created = self.updated
        super(MpesaBase, self).save(*args, **kwargs)
        return self

    def __str__(self):
        return "{}".format(self.code)

    def extra_data(self) -> dict:
        """Return extra column of the entity as json"""
        return utils.to_json(self.extra)

    def was_registered_recently(self):
        """Check latest entity"""
        return self.created >= utils.kenya_time() - datetime.timedelta(days=1)

    def was_updated_recently(self):
        """Check latest entity"""
        return self.updated >= utils.kenya_time() - datetime.timedelta(days=1)

    was_updated_recently.admin_order_field = 'pub_date'
    was_updated_recently.boolean = True
    was_updated_recently.short_description = 'Updated recently?'


class APILog(FlatModel):
    """Used for tracking MPESA API interactions
    """
    ref = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    extra = models.TextField(null=True, blank=True, help_text="important data")
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)

    class Meta:
        """Associate the model to the app"""
        app_label = "mpesapy"

    def __str__(self):
        return "{}".format(self.ref)

    def save(self, *args, **kwargs):
        """Saving entity logic"""
        self.updated = utils.kenya_time()
        if isinstance(self.extra, dict):
            self.extra = utils.from_json(self.extra)
        if self._state.adding:
            if kwargs.get("created"):
                self.created = kwargs.get("created")
            else:
                self.created = self.updated
        super(APILog, self).save(*args, **kwargs)
        return self

    @classmethod
    def create(
            cls,
            business_number: str,
            extra_data: dict = None,
            **kwargs):
        """entity creator helper"""
        extra_data = {} if extra_data is None else extra_data
        log = cls(**kwargs).save()
        log.ref = "{}.{}".format(
            business_number,
            conversion.baseconvert(log.id, conversion.BASE10,
                                   conversion.BASE62))
        if extra_data:
            log.extra = utils.from_json(extra_data)
        return log.save()

    def extra_data(self) -> dict:
        """Return extra column of the entity as json"""
        return utils.to_json(self.extra)

    def was_registered_recently(self):
        """Check latest entity"""
        return self.created >= utils.kenya_time() - datetime.timedelta(days=1)

    def was_updated_recently(self):
        """Check latest entity"""
        return self.updated >= utils.kenya_time() - datetime.timedelta(days=1)

    was_updated_recently.admin_order_field = 'pub_date'
    was_updated_recently.boolean = True
    was_updated_recently.short_description = 'Updated recently?'
