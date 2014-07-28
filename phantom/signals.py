from django.dispatch import Signal

__author__ = 'bespider'

signup_complete = Signal(providing_args=["user", ])
password_complete = Signal(providing_args=["user", ])
