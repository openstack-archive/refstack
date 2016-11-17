# Copyright (c) 2015 Mirantis, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Authentication controller."""

from oslo_config import cfg
import pecan
from pecan import rest
from six.moves.urllib import parse

from refstack.api import constants as const
from refstack.api import utils as api_utils
from refstack import db


OPENID_OPTS = [
    cfg.StrOpt('openstack_openid_endpoint',
               default='https://openstackid.org/accounts/openid2',
               help='OpenStackID Auth Server URI.'
               ),
    cfg.StrOpt('openid_logout_endpoint',
               default='https://openstackid.org/accounts/user/logout',
               help='OpenStackID logout URI.'
               ),
    cfg.StrOpt('openid_mode',
               default='checkid_setup',
               help='Interaction mode. Specifies whether Openstack Id '
                    'IdP may interact with the user to determine the '
                    'outcome of the request.'
               ),
    cfg.StrOpt('openid_ns',
               default='http://specs.openid.net/auth/2.0',
               help='Protocol version. Value identifying the OpenID '
                    'protocol version being used. This value should '
                    'be "http://specs.openid.net/auth/2.0".'
               ),
    cfg.StrOpt('openid_return_to',
               default='/v1/auth/signin_return',
               help='Return endpoint in Refstack\'s API. Value indicating '
                    'the endpoint where the user should be returned to after '
                    'signing in. Openstack Id Idp only supports HTTPS '
                    'address types.'
               ),
    cfg.StrOpt('openid_claimed_id',
               default='http://specs.openid.net/auth/2.0/identifier_select',
               help='Claimed identifier. This value must be set to '
                    '"http://specs.openid.net/auth/2.0/identifier_select". '
                    'or to user claimed identity (user local identifier '
                    'or user owned identity [ex: custom html hosted on a '
                    'owned domain set to html discover]).'
               ),
    cfg.StrOpt('openid_identity',
               default='http://specs.openid.net/auth/2.0/identifier_select',
               help='Alternate identifier. This value must be set to '
                    'http://specs.openid.net/auth/2.0/identifier_select.'
               ),
    cfg.StrOpt('openid_ns_sreg',
               default='http://openid.net/extensions/sreg/1.1',
               help='Indicates request for user attribute information. '
                    'This value must be set to '
                    '"http://openid.net/extensions/sreg/1.1".'
               ),
    cfg.StrOpt('openid_sreg_required',
               default='email,fullname',
               help='Comma-separated list of field names which, '
                    'if absent from the response, will prevent the '
                    'Consumer from completing the registration without '
                    'End User interation. The field names are those that '
                    'are specified in the Response Format, with the '
                    '"openid.sreg." prefix removed. Valid values include: '
                    '"country", "email", "firstname", "language", "lastname"'
               )
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='osid',
                         title='Options for the Refstack OpenID 2.0 through '
                               'Openstack Authentication Server')
CONF.register_group(opt_group)
CONF.register_opts(OPENID_OPTS, opt_group)


class AuthController(rest.RestController):
    """Controller provides user authentication in OpenID 2.0 IdP."""

    _custom_actions = {
        "signin": ["GET"],
        "signin_return": ["GET"],
        "signout": ["GET"]
    }

    def _auth_failure(self, message):
        params = {
            'message': message
        }
        url = parse.urljoin(CONF.ui_url,
                            '/#/auth_failure?' + parse.urlencode(params))
        pecan.redirect(url)

    @pecan.expose()
    def signin(self):
        """Handle signin request."""
        session = api_utils.get_user_session()
        if api_utils.is_authenticated():
            pecan.redirect(CONF.ui_url)
        else:
            api_utils.delete_params_from_user_session([const.USER_OPENID])

        csrf_token = api_utils.get_token()
        session[const.CSRF_TOKEN] = csrf_token
        session.save()
        return_endpoint = parse.urljoin(CONF.api.api_url,
                                        CONF.osid.openid_return_to)
        return_to = api_utils.set_query_params(return_endpoint,
                                               {const.CSRF_TOKEN: csrf_token})

        params = {
            const.OPENID_MODE: CONF.osid.openid_mode,
            const.OPENID_NS: CONF.osid.openid_ns,
            const.OPENID_RETURN_TO: return_to,
            const.OPENID_CLAIMED_ID: CONF.osid.openid_claimed_id,
            const.OPENID_IDENTITY: CONF.osid.openid_identity,
            const.OPENID_REALM: CONF.api.api_url,
            const.OPENID_NS_SREG: CONF.osid.openid_ns_sreg,
            const.OPENID_NS_SREG_REQUIRED: CONF.osid.openid_sreg_required,
        }
        url = CONF.osid.openstack_openid_endpoint
        url = api_utils.set_query_params(url, params)
        pecan.redirect(location=url)

    @pecan.expose()
    def signin_return(self):
        """Handle returned request from OpenID 2.0 IdP."""
        session = api_utils.get_user_session()
        if pecan.request.GET.get(const.OPENID_ERROR):
            api_utils.delete_params_from_user_session([const.CSRF_TOKEN])
            self._auth_failure(pecan.request.GET.get(const.OPENID_ERROR))

        if pecan.request.GET.get(const.OPENID_MODE) == 'cancel':
            api_utils.delete_params_from_user_session([const.CSRF_TOKEN])
            self._auth_failure('Authentication canceled.')

        session_token = session.get(const.CSRF_TOKEN)
        request_token = pecan.request.GET.get(const.CSRF_TOKEN)
        if request_token != session_token:
            api_utils.delete_params_from_user_session([const.CSRF_TOKEN])
            self._auth_failure('Authentication failed. Please try again.')

        api_utils.verify_openid_request(pecan.request)
        user_info = {
            'openid': pecan.request.GET.get(const.OPENID_CLAIMED_ID),
            'email': pecan.request.GET.get(const.OPENID_NS_SREG_EMAIL),
            'fullname': pecan.request.GET.get(const.OPENID_NS_SREG_FULLNAME)
        }
        user = db.user_save(user_info)

        api_utils.delete_params_from_user_session([const.CSRF_TOKEN])
        session[const.USER_OPENID] = user.openid
        session.save()

        pecan.redirect(CONF.ui_url)

    @pecan.expose('json')
    def signout(self):
        """Handle signout request."""
        if api_utils.is_authenticated():
            api_utils.delete_params_from_user_session([const.USER_OPENID])

        params = {
            'openid_logout': CONF.osid.openid_logout_endpoint
        }
        url = parse.urljoin(CONF.ui_url,
                            '/#/logout?' + parse.urlencode(params))
        pecan.redirect(url)
