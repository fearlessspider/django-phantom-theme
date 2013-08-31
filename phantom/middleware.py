try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

__author__ = 'fearless'


class PopupMiddleware(object):
    """
    Place it **before** the :class:`django.middleware.common.CommonMiddleware`
    in your ``MIDLEWARE_CLASSESS`` setting.

    phantom.core builds upon the original django admin application.
    Some admin widgets open pop-up windows where phantom.core uses
    a modal window. Since original AdminModel views attempt to return
    pop-up window values to the parent through the ``opener`` javascript
    variable.
    This middleare implements an easy fix, replacing ``opener`` with
    the ``parent`` variable, which is appropriate for iframes.
    """
    def process_response(self, request, resp):
        """
        This method is called right after a view is processed and has
        returned an HttpResponse object.
        """

        #responses will not always have a content attribute starting
        #from Django 1.5
        if resp.status_code == 200 and \
            hasattr(resp, 'content') and \
            resp.content.startswith('<!DOCTYPE html><html><head>'
                                    '<title></title></head><body>'
                                    '<script type="text/javascript">'
                                    'opener.dismissAddAnotherPopup(window,'):

            resp.content = resp.content.\
                replace('<!DOCTYPE html><html><head><title></title></head>'
                        '<body><script type="text/javascript">'
                        'opener.dismissAddAnotherPopup(window,',
                        '<!DOCTYPE html><html><head><title></title></head>'
                        '<body><script>parent.dismissAddAnotherPopup(window,')
        return resp

