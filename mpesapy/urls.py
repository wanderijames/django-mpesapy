"""Main app urls"""
# pylint: disable=invalid-name
from django.urls import (include, path)
from mpesapy.v1 import views as ipn_views

urlpatterns = [
    # left intact for backward compatibility
    path('c2b_bill/', ipn_views.c2b_paybill, name='c2b_paybill'),
    # left intact for backward compatibility
    path('c2b_buy/', ipn_views.c2b_buy_goods, name='c2b_buy_goods'),
    path('v1/', include('mpesapy.v1.urls')),
    path('v2/', include('mpesapy.v2.urls')),
]
