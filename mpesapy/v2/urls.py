"""URLS conf for the v2 sub app"""
# pylint: disable=invalid-name
# pylint: disable=line-too-long
from django.urls import re_path
from mpesapy.v2 import views

urlpatterns = [
    re_path(r'^validate/(?P<business>([a-zA-Z0-9])+)/c2b', views.c2b_validation, name='c2b_validate'),
    re_path(r'^confirm/(?P<business>([a-zA-Z0-9])+)/c2b', views.c2b_confirmation, name='c2b_confirmation'),
]
