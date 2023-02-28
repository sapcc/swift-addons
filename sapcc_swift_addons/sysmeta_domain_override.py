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
from swift.common.utils import get_logger

SYSMETA_HEADER = get_sys_meta_prefix("account") + "project-domain-id"
OVERRIDE_HEADER = "x-account-project-domain-id-override"


class DomainOverrideMiddleware:
    """
    Middleware that allows you to override the 'X-Account-Sysmeta-Project-Domain-Id' for
    an account by providing the 'X-Account-Project-Domain-Id-Override' header.

    Example: we use this in Limes during account creation after project quota is set:
    https://github.com/sapcc/limes/blob/48d140aa62e099bd68f8692a4d33a6d7ea5f0077/internal/plugins/swift.go#L196
    """

    def __init__(self, app, conf, logger=None):
        self.app = app
        self.logger = logger or get_logger(conf, log_route="sysmeta_domain_override")

    def __call__(self, env, start_response):
        # only reseller may invoke the override
        if env.get("reseller_request", False):
            req = Request(env)
            if OVERRIDE_HEADER in req.headers:
                req.headers[SYSMETA_HEADER] = req.headers[OVERRIDE_HEADER]

        # we now continue with our regularly scheduled programming
        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    """
    Standard filter factory to use the middleware with paste.deploy.
    """
    conf = global_conf.copy()
    conf.update(local_conf)

    def sysmeta_domain_override_filter(app):
        return DomainOverrideMiddleware(app, conf)

    return sysmeta_domain_override_filter
