from babel.numbers import get_currency_symbol
from babeldjango.middleware import get_current_locale
from babeldjango.templatetags.babel import babel
from django.forms import TextInput, RadioSelect, SelectMultiple, Select
from django.utils.safestring import mark_safe
from django.utils.translation import to_locale, get_language

try:
    from pytz import timezone
except ImportError:
    timezone = None

__author__ = 'fearless'


class AutoCompleteTextInput(TextInput):

    def __init__(self, *args, **kwargs):
        if 'source' in kwargs:
            self.source = kwargs['source']
            del kwargs['source']
        else:
            self.source = None
        super(AutoCompleteTextInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        if self.source:
            attrs['autocomplete'] = 'off'
        output = super(AutoCompleteTextInput, self).render(name, value, attrs)
        if self.source:
            js = '<script>(function($){$("#%(id)s").typeahead({source: ' \
                'function(query, process) { $.get("%(source)s", {query: ' \
                'query},function(data) { return typeof data.results == ' \
                '"undefined" ? false : process(data.results); }, "json") ' \
                '}});})(phantom.jQuery);</script>' % {'id': attrs['id'],
                                                        'source': self.source}
        return output + mark_safe(js)


class BootstrapRadioRenderer(RadioSelect.renderer):
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % unicode(w).replace('<label ', '<label class="radio inline" ') for w in self])+'&#xa0;')


class BootstrapCurrencyDecimalWidget(TextInput):
    user = None

    def __init__(self, *args, **kwargs):
        super(BootstrapCurrencyDecimalWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        u"""Render base widget and add bootstrap spans"""
        field = super(BootstrapCurrencyDecimalWidget, self).render(name, value, attrs)
        settingObj = None
        if self.user:
            settingObj = self.user.get_profile().currency
        currency = 'USD'
        if settingObj:
            currency = settingObj
        locale = get_current_locale()
        if not locale:
            Locale = babel.core.Locale
            locale = Locale.parse(to_locale(get_language()))
        return mark_safe((
            u'<div class="input-group">'
            u'    <span class="input-group-addon">%(data)s</span>%(field)s'
            u'</div>'
        ) % {'field': field, 'data': get_currency_symbol(currency, locale)})


class BootstrapPercentageDecimalWidget(TextInput):
    def render(self, name, value, attrs=None):
        u"""Render base widget and add bootstrap spans"""
        field = super(BootstrapPercentageDecimalWidget, self).render(name, value, attrs)
        return mark_safe((
            u'<div class="input-group">'
            u'%(field)s'
            u'    <span class="input-group-addon">%(data)s</span>'
            u'</div>'
        ) % {'field': field, 'data': '%'})


class URLThumbWidget(TextInput):
    def render(self, name, value, attrs=None):
        u"""Render base widget and add bootstrap spans"""
        field = super(URLThumbWidget, self).render(name, value, attrs)
        return mark_safe((
            u'<div class="input-group">'
            u'    <span class="input-group-addon"><img src="%(data)s"></span>'
            u'%(field)s'
            u'</div>'
        ) % {'field': field, 'data': value})


class Select2MultipleWidget(SelectMultiple):

    class Media:
        css = {'all': ('phantom/css/select2/select2.css',)}
        js = ('phantom/css/select2/select2.min.js',)

    def render(self, name, value, attrs=None, choices=()):
        result = super(Select2MultipleWidget, self).render(name, value, attrs, choices)
        return result + mark_safe('<script>(function($){'\
                                  '$(\'#%s\').select2();'\
                                  '})(phantom.jQuery);</script>' % attrs['id'])


class Select2Widget(Select):
    select2_options = ''

    class Media:
        css = {'all': ('phantom/css/select2/select2.css',)}
        js = ('phantom/css/select2/select2.min.js',)

    def render(self, name, value, attrs=None, choices=()):
        result = super(Select2Widget, self).render(name, value, attrs, choices)
        return result + mark_safe('<script>(function($){'\
                                  '$(\'#%s\').select2(%s);'\
                                  '})(phantom.jQuery);</script>' % (attrs['id'],
                                                                      self.select2_options))
