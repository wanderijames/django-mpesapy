"""Admin views for the app"""
from django.contrib import admin
import mpesapy.models as mdl


@admin.register(mdl.MpesaCtoBill)
class MpesaCtoBillAdmin(admin.ModelAdmin):
    """Admin entities view for MpesaCtoBill"""
    list_display = ('mpesa_code', 'mpesa_amt', 'mpesa_msisdn', 'mpesa_sender')


@admin.register(mdl.MpesaCtoBuy)
class MpesaCtoBuyAdmin(admin.ModelAdmin):
    """Admin entities view for MpesaCtoBuy"""
    list_display = ('mpesa_code', 'mpesa_amt', 'mpesa_msisdn', 'mpesa_sender')


@admin.register(mdl.Business)
class BusinessSEAdmin(admin.ModelAdmin):
    """Admin entities view for Business"""
    list_display = ('number', 'name', 'bnt')


@admin.register(mdl.MpesaBase)
class MpesaBaseAdmin(admin.ModelAdmin):
    """Admin entities view for MpesaBase"""
    list_display = ('code', 'amount', 'msisdn', 'person', 'created', 'updated')


@admin.register(mdl.APILog)
class APILogAdmin(admin.ModelAdmin):
    """Admin entities view for APILog"""
    list_display = ('ref', 'created', 'updated')
