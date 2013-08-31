from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.utils.translation import ugettext as _
from phantom.forms import ChangeEmailForm, EditProfileForm

__author__ = 'fearless'


class OptionView(TemplateView):
    template_name = 'admin/options.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('phantom.change_option'):
            raise PermissionDenied
        return super(OptionView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the
        form. Copied form the generic FormView class-based view
        """
        kwargs = {}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data':self.request.POST,
                'files':self.request.FILES,
                })
        return kwargs

    def get_context_data(self, **kwargs):
        from phantom import admin_site
        context = super(OptionView, self).get_context_data(**kwargs)
        context['optionset_admin'] = admin_site.get_optionset_admin(self.kwargs['optionset_label'])(**self.get_form_kwargs())
        context['title'] = '%s' % (unicode(context['optionset_admin'].verbose_name))
        return context

    def post(self, request, *args, **kwargs):
        """
        Validate the form and save the options upon success
        """
        context = self.get_context_data()
        if context['optionset_admin'].form.is_valid():
            context['optionset_admin'].save()
            messages.add_message(self.request, messages.SUCCESS, _('The options were succesfully saved.'))
        return self.render_to_response(context)

    def put(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class EmailChangeView(View):
    form_class = ChangeEmailForm
    template_name = 'admin/auth/user/email_form.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.request.user, request.POST)

        if form.is_valid():
            form.save()

            messages.success(request, _('You have received an email at' + self.request.user.email + '.'))
        return render(request, self.template_name, {'form': form})

    def get(self, request, *args, **kwargs):
        form = self.form_class(user=self.request.user)
        return render(request, self.template_name, {'form': form})


class AccountView(View):
    form_class = EditProfileForm
    template_name = 'admin/auth/user/account.html'

    def __init__(self, *args, **kwargs):
        super(AccountView, self).__init__(*args, **kwargs)
        self.success_url = reverse('admin:my-account')

    def post(self, request, *args, **kwargs):
        user = request.user
        profile = user.get_profile()
        user_initial = {'first_name': user.first_name,
                    'last_name': user.last_name}
        form = self.form_class(request.POST, request.FILES, instance=profile,
                                 initial=user_initial)
        if form.is_valid():
            form.instance.user = self.request.user
            form.save()

            messages.success(request,
                             _('Account updated.'))
        return render(request, self.template_name, {'form': form})

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = user.get_profile()
        user_initial = {'first_name': user.first_name,
                    'last_name': user.last_name}
        form = self.form_class(instance=profile, initial=user_initial)
        return render(request, self.template_name, {'form':form})

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, _('Your account has been updated successfuly.'))
        return super(AccountView, self).form_valid(form)

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        context['title'] = _('My account')
        return context
