from django.conf.urls import url
from mpesapy.v1 import views

urlpatterns = [
    url(r'^c2b_bill', views.c2b_paybill, name='c2b_bill'),
    url(r'^c2b_buy', views.c2b_buy_goods, name='c2b_till'),
]
