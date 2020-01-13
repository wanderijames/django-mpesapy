"""app config init"""
from __future__ import unicode_literals

from django.apps import AppConfig


class MpesaConfig(AppConfig):
    """Initialization"""
    # pylint: disable=unused-variable
    name = 'mpesapy'

    def ready(self):
        from mpesapy import signals  # NOQA
