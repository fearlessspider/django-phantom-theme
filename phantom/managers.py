import re

from django.db import models
from django.contrib.auth.models import User, UserManager

from phantom.user_utils import generate_sha1, get_profile_model, get_datetime_now
import phantom.signals as user_signals


__author__ = 'bespider'

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class UserManager(UserManager):
    """ Extra functionality for the User model. """

    def create_user(self, username, email, password, active=False,
                    send_email=True):
        """
        A simple wrapper that creates a new :class:`User`.

        :param username:
            String containing the username of the new user.

        :param email:
            String containing the email address of the new user.

        :param password:
            String containing the password for the new user.

        :param active:
            Boolean that defines if the user requires activation by clicking
            on a link in an e-mail. Defaults to ``False``.

        :param send_email:
            Boolean that defines if the user should be sent an email. You could
            set this to ``False`` when you want to create a user in your own
            code, but don't want the user to activate through email.

        :return: :class:`User` instance representing the new user.

        """
        now = get_datetime_now()

        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = active
        new_user.save()

        user_profile = self.create_user_profile(new_user)

        # All users have an empty profile
        profile_model = get_profile_model()
        try:
            new_profile = new_user.get_profile()
        except profile_model.DoesNotExist:
            new_profile = profile_model(user=new_user)
            new_profile.save(using=self._db)

        if send_email:
            user_profile.send_activation_email()

        return new_user

    def create_user_profile(self, user):
        """
        Creates an :class:`UserSignup` instance for this user.

        :param user:
            Django :class:`User` instance.

        :return: The newly created :class:`UserSignup` instance.

        """
        if isinstance(user.username, unicode):
            user.username = user.username.encode('utf-8')
        salt, activation_key = generate_sha1(user.username)

        return self.create(user=user,
                           activation_key=activation_key)

    def activate_user(self, activation_key):
        """
        Activate an :class:`User` by supplying a valid ``activation_key``.

        If the key is valid and an user is found, activates the user and
        return it. Also sends the ``activation_complete`` signal.

        :param activation_key:
            String containing the secret SHA1 for a valid activation.

        :return:
            The newly activated :class:`User` or ``False`` if not successful.

        """
        print activation_key
        if SHA1_RE.search(activation_key):
            try:
                mssuser = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not mssuser.activation_key_expired():
                mssuser.activation_key = True
                user = mssuser.user
                user.is_active = True
                mssuser.save(using=self._db)
                user.save(using=self._db)

                # Send the activation_complete signal
                user_signals.activation_complete.send(sender=None,
                                                      user=user)

                return user
        return False

    def confirm_email(self, confirmation_key):
        """
        Confirm an email address by checking a ``confirmation_key``.

        A valid ``confirmation_key`` will set the newly wanted e-mail
        address as the current e-mail address. Returns the user after
        success or ``False`` when the confirmation key is
        invalid. Also sends the ``confirmation_complete`` signal.

        :param confirmation_key:
            String containing the secret SHA1 that is used for verification.

        :return:
            The verified :class:`User` or ``False`` if not successful.

        """
        if SHA1_RE.search(confirmation_key):
            try:
                mssuser = self.get(email_confirmation_key=confirmation_key,
                                   email_unconfirmed__isnull=False)
            except self.model.DoesNotExist:
                return False
            else:
                user = mssuser.user
                old_email = user.email
                user.email = mssuser.email_unconfirmed
                mssuser.email_unconfirmed, mssuser.email_confirmation_key = '', ''
                mssuser.save(using=self._db)
                user.save(using=self._db)

                # Send the confirmation_complete signal
                user_signals.confirmation_complete.send(sender=None,
                                                        user=user,
                                                        old_email=old_email)

                return user
        return False

    def delete_expired_users(self):
        """
        Checks for expired users and delete's the ``User`` associated with
        it. Skips if the user ``is_staff``.

        :return: A list containing the deleted users.

        """
        deleted_users = []
        for user in User.objects.filter(is_staff=False,
                                        is_active=False):
            if user.user_signup.activation_key_expired():
                deleted_users.append(user)
                user.delete()
        return deleted_users


class UserBaseProfileManager(models.Manager):
    """ Manager for :class:`UserProfile` """

    def get_visible_profiles(self, user=None):
        """
        Returns all the visible profiles available to this user.

        For now keeps it simple by just applying the cases when a user is not
        active, a user has it's profile closed to everyone or a user only
        allows registered users to view their profile.

        :param user:
            A Django :class:`User` instance.

        :return:
            All profiles that are visible to this user.

        """
        profiles = self.all()

        filter_kwargs = {'user__is_active': True}

        profiles = profiles.filter(**filter_kwargs)
        return profiles
