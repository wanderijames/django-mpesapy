from __future__ import unicode_literals

from django.apps import AppConfig


class MpesaConfig(AppConfig):
    name = 'mpesapy'

    def ready(self):
        from mpesapy import signals
