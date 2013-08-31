import re
from django.core.exceptions import ValidationError
from django.db import models

__author__ = 'fearless'


class OptionNameField(models.CharField):

    def clean(self, value):
        value = super(OptionNameField, self).clean(value)
        if not re.match(r'[a-zA-Z_]+', value):
            raise ValidationError('Only letters and underscores are allowed.')
        return value