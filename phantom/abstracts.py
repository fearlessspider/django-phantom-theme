# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _
from phantom.fields import OptionNameField
from phantom.managers import UserBaseProfileManager

try:
    from pytz import timezone
except ImportError:
    timezone = None

babel = __import__('babel', {}, {}, ['core', 'support'])
Format = babel.support.Format
Locale = babel.core.Locale

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


class AbstractProfile(models.Model):
    """ Base model needed for extra profile functionality """

    user = models.OneToOneField('auth.User')

    # Preferences
    CURRENCY = (
        ("USD","USD"),
        ("EUR","EUR"),
        ("GBP","GBP"),
        ("PLN","PLN")
    )
    currency = models.CharField(choices=CURRENCY, default="USD", max_length=3)

    objects = UserBaseProfileManager()

    class Meta:
        """
        Meta options making the model abstract and defining permissions.

        The model is ``abstract`` because it only supplies basic functionality
        to a more custom defined model that extends it. This way there is not
        another join needed.

        We also define custom permissions because we don't know how the model
        that extends this one is going to be called. So we don't know what
        permissions to check. For ex. if the user defines a profile model that
        is called ``MyProfile``, than the permissions would be
        ``add_myprofile`` etc. We want to be able to always check
        ``add_profile``, ``change_profile`` etc.

        """
        abstract = True

    def __unicode__(self):
        return 'Profile of %(username)s' % {'username': self.user.username}

    def get_full_name_or_username(self):
        """
        Returns the full name of the user, or if none is supplied will return
        the username.

        :return:
            ``String`` containing the full name of the user.

        """
        user = self.user
        if user.first_name or user.last_name:
            # We will return this as translated string. Maybe there are some
            # countries that first display the last name.
            name = _("%(first_name)s %(last_name)s") % \
                   {'first_name': user.first_name,
                    'last_name': user.last_name}
        else:
            name = "%(email)s" % {'email': user.email}
        return name.strip()
