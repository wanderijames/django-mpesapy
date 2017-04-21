from django.conf.urls import url
from mpesapy.v2 import views

urlpatterns = [
    url(r'^validate/(?P<business>([a-zA-Z0-9])+)/c2b', views.c2b_validation,
        name='c2b_validate'),
    url(r'^confirm/(?P<business>([a-zA-Z0-9])+)/c2b', views.c2b_confirmation,
        name='c2b_confirmation'),
]
