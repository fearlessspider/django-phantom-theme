# -*- coding: utf-8 -*-
from django.contrib.auth import models as auth_models
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _
from phantom.fields import OptionNameField
from phantom.managers import UserManager


__author__ = 'fearless'


class AbstractOption(models.Model):
    """
    Abstract model for Phantom option
    """
    optionset_label = models.CharField(max_length=50)
    name = OptionNameField(max_length=50)
    value = models.TextField(null=True)
    lang_dependant = models.BooleanField(default=False)

    class Meta:
        abstract = True
        unique_together = ('optionset_label', 'name')
        ordering = ['optionset_label', 'lang_dependant']

    def __unicode__(self):
        return u'%s.%s' % (self.optionset_label, self.name)


class AbstractUser(auth_models.AbstractBaseUser,
                   auth_models.PermissionsMixin):
    """
    An abstract base user suitable for use in Oscar projects.

    This is basically a copy of the core AbstractUser model but without a
    username field
    """
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(
        _('First name'), max_length=255, blank=True)
    last_name = models.CharField(
        _('Last name'), max_length=255, blank=True)
    is_staff = models.BooleanField(
        _('Staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(
        _('Active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'),
                                       default=timezone.now)

    # Preferences
    CURRENCY = (
        ("USD","USD"),
        ("EUR","EUR"),
        ("GBP","GBP"),
        ("PLN","PLN")
    )
    currency = models.CharField(choices=CURRENCY, default="USD", max_length=3)
    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        abstract = True

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

