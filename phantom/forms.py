from django import forms
from django.contrib.auth.forms import PasswordChangeForm, ReadOnlyPasswordHashField, UserChangeForm, UserCreationForm
from django.forms import models
from phantom.models import User
from django.core.urlresolvers import reverse
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext as _

attrs_dict = {'class': 'required'}

USERNAME_RE = r'^[\.\w]+$'

__author__ = 'fearless'


class PopupInlineFormSet(BaseInlineFormSet):
    changed_objects = []
    deleted_objects = []
    new_objects = []

    def is_valid(self):
        """
        Do not validate any forms, no forms actually exist
        """
        return True

    def get_add_url(self):
        return '%s?fk_name=%s&fk_id=%s' % (reverse('admin:%s_%s_add' % \
            (self.model._meta.app_label, self.model._meta.object_name.lower())),
                                  self.fk.name,
                                  self.instance.pk)

    def get_change_url(self, obj_id):
        return '%s?fk_name=%s' % (reverse('admin:%s_%s_change' % \
            (self.model._meta.app_label, self.model._meta.object_name.lower()),
            args=(obj_id,)),
                                  self.fk.name)

    def get_delete_url(self, obj_id):
        return reverse('admin:%s_%s_deleteit' % (self.model._meta.app_label,
                                                 self.model._meta.object_name.lower()),
                       args=(obj_id,))

    def get_reorder_url(self):
        return reverse('admin:%s_%s_inlinereorder' % (self.model._meta.app_label,
                                                 self.model._meta.object_name.lower()))

    def save(self, commit=True):
        """
        Override save_new to do nothing, as everything is handled by ajax requests.
        """
        return True


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_(u"New email"))

    def __init__(self, user, *args, **kwargs):
        """
        The current ``user`` is needed for initialisation of this form so
        that we can check if the email address is still free and not always
        returning ``True`` for this query because it's the users own e-mail
        address.

        """
        super(ChangeEmailForm, self).__init__(*args, **kwargs)
        if not isinstance(user, User):
            raise TypeError, "user must be an instance of User"
        else:
            self.user = user

    def clean_email(self):
        """ Validate that the email is not already registered with another user """
        if self.cleaned_data['email'].lower() == self.user.email:
            raise forms.ValidationError(_(u'You\'re already known under this email.'))
        if User.objects.filter(email__iexact=self.cleaned_data['email']).exclude(email__iexact=self.user.email):
            raise forms.ValidationError(_(u'This email is already in use. Please supply a different email.'))
        return self.cleaned_data['email']

    def save(self):
        """
        Save method calls :func:`user.change_email()` method which sends out an
        email with an verification key to verify and with it enable this new
        email address.

        """
        return self.user.user_signup.change_email(self.cleaned_data['email'])


class PhantomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label=_("Old password"),
                                   widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput(attrs={'class':'form-control'}))


class PhantomUserChangeForm(models.ModelForm):
    email = forms.RegexField(
        label=_("Email"), max_length=30, regex=r"^[\w.@+-]+$",
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")}, widget=forms.TextInput(attrs={'class':'form-control'}))
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PhantomUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class PhantomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    email = forms.RegexField(label=_("Email"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")}, widget=forms.TextInput(attrs={'class':'form-control'}))
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        help_text=_("Enter the same password as above, for verification."))
