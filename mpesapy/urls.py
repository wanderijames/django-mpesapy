from django.conf.urls import url, patterns

from mpesapy import views as ipn_views

urlpatterns = patterns('',
                       url(r'^c2b_bill', ipn_views.c2b_paybill, name='c2b_paybill'),
                       url(r'^c2b_buy', ipn_views.c2b_buy_goods, name='c2b_buy_goods'))
