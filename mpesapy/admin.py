from django.contrib import admin
from mpesapy.models import *


class MpesaCtoBillAdmin(admin.ModelAdmin):
    list_display = ('mpesa_code', 'mpesa_amt', 'mpesa_msisdn', 'mpesa_sender')


class MpesaCtoBuyAdmin(admin.ModelAdmin):
    list_display = ('mpesa_code', 'mpesa_amt', 'mpesa_msisdn', 'mpesa_sender')


admin.site.register(MpesaCtoBill, MpesaCtoBillAdmin)
admin.site.register(MpesaCtoBuy, MpesaCtoBuyAdmin)
