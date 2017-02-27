# Copyright 2017 SAP SE
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from swift.common.request_helpers import get_sys_meta_prefix
from swift.common.swob import Request

SYSMETA_HEADER  = get_sys_meta_prefix('account') + 'project-domain-id'
OVERRIDE_HEADER = 'x-account-project-domain-id-override'

class DomainOverrideMiddleware(object):
    def __init__(self, app):
        self.app = app

    @classmethod
    def factory(cls, global_config, **local_config):
        def _factory(app):
            return cls(app, **local_config)

        return _factory

    def __call__(self, environ, start_response):
        # only reseller may invoke the override
        if environ.get('reseller_request', False):
            req = Request(environ)
            if OVERRIDE_HEADER in req.headers:
                req.headers[SYSMETA_HEADER] = req.headers[OVERRIDE_HEADER]

        # we now continue with our regularly scheduled programming
        return self.app(environ, start_response)
