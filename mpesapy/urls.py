from django.conf.urls import (include, url)
from mpesapy.v1 import views as ipn_views

urlpatterns = [
    # left intact for backward compatibility
    url(r'^c2b_bill', ipn_views.c2b_paybill, name='c2b_paybill'),
    # left intact for backward compatibility
    url(r'^c2b_buy', ipn_views.c2b_buy_goods, name='c2b_buy_goods'),
    url(r'^v1/', include('mpesapy.v1.urls')),
    url(r'^v2/', include('mpesapy.v2.urls')),
]
