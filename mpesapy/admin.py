from django.contrib import admin
import mpesapy.models as mdl


@admin.register(mdl.MpesaCtoBill)
class MpesaCtoBillAdmin(admin.ModelAdmin):
    list_display = ('mpesa_code', 'mpesa_amt', 'mpesa_msisdn', 'mpesa_sender')


@admin.register(mdl.MpesaCtoBuy)
class MpesaCtoBuyAdmin(admin.ModelAdmin):
    list_display = ('mpesa_code', 'mpesa_amt', 'mpesa_msisdn', 'mpesa_sender')


@admin.register(mdl.Business)
class BusinessSEAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'bnt')


@admin.register(mdl.MpesaBase)
class MpesaBaseAdmin(admin.ModelAdmin):
    list_display = ('code', 'amount', 'msisdn', 'person', 'created', 'updated')


@admin.register(mdl.APILog)
class APILogAdmin(admin.ModelAdmin):
    list_display = ('ref', 'created', 'updated')
