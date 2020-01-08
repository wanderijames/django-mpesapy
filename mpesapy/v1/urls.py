"""Sub-app urls"""
# pylint: disable=invalid-name
from django.urls import re_path
from mpesapy.v1 import views

urlpatterns = [
    re_path(r'^c2b_bill', views.c2b_paybill, name='c2b_bill'),
    re_path(r'^c2b_buy', views.c2b_buy_goods, name='c2b_till'),
]
