##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Class: HTTPBasicAuthHelper
"""

from AccessControl.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo

from zope.interface import Interface

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import \
        ILoginPasswordHostExtractionPlugin
from Products.PluggableAuthService.interfaces.plugins import \
        IChallengePlugin
from Products.PluggableAuthService.interfaces.plugins import \
        ICredentialsResetPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements


manage_addHTTPBasicAuthHelperForm = PageTemplateFile(
    'www/hbAdd', globals(), __name__='manage_addHTTPBasicAuthHelperForm')


class IHTTPBasicAuthHelper(Interface):
    """ Marker interface.
    """


def addHTTPBasicAuthHelper(dispatcher, id, title=None, REQUEST=None):

    """ Add a HTTP Basic Auth Helper to a Pluggable Auth Service.
    """
    sp = HTTPBasicAuthHelper(id, title)
    dispatcher._setObject(sp.getId(), sp)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect('%s/manage_workspace'
                                     '?manage_tabs_message='
                                     'HTTPBasicAuthHelper+added.' %
                                     dispatcher.absolute_url())


class HTTPBasicAuthHelper(BasePlugin):

    """ Multi-plugin for managing details of HTTP Basic Authentication.
    """
    meta_type = 'HTTP Basic Auth Helper'
    security = ClassSecurityInfo()
    protocol = "http"  # The PAS challenge 'protocol' we use.

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    @security.private
    def extractCredentials(self, request):

        """ Extract basic auth credentials from 'request'.
        """
        creds = {}
        login_pw = request._authUserPW()

        if login_pw is not None:
            name, password = login_pw

            creds['login'] = name
            creds['password'] = password
            creds['remote_host'] = request.get('REMOTE_HOST', '')

            try:
                creds['remote_address'] = request.getClientAddr()
            except AttributeError:
                creds['remote_address'] = ''

        return creds

    @security.private
    def challenge(self, request, response, **kw):

        """ Challenge the user for credentials.
        """
        realm = response.realm
        if realm:
            response.addHeader('WWW-Authenticate', 'basic realm="%s"' % realm)
        m = "<strong>You are not authorized to access this resource.</strong>"

        response.setBody(m, is_error=1)
        response.setStatus(401)
        return 1

    @security.private
    def resetCredentials(self, request, response):

        """ Raise unauthorized to tell browser to clear credentials.
        """
        # XXX:  Does this need to check whether we have an HTTP response?
        response.unauthorized()


classImplements(HTTPBasicAuthHelper, IHTTPBasicAuthHelper,
                ILoginPasswordHostExtractionPlugin,
                IChallengePlugin, ICredentialsResetPlugin)

InitializeClass(HTTPBasicAuthHelper)
