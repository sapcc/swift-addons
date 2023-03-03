# Copyright 2023 SAP SE
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

from swift.common.constraints import (
    check_account_format,
    check_container_format,
    valid_api_version,
)
from swift.common.request_helpers import check_path_header, get_user_meta_prefix
from swift.common.swob import HTTPMethodNotAllowed, Request, wsgi_unquote
from swift.common.utils import config_true_value, get_logger, list_from_csv
from swift.proxy.controllers.base import get_info


class WriteRestrictionMiddleware:
    """
    Middleware that restricts writes to a container to a set of specific roles.
    """

    def __init__(self, app, conf, logger=None):
        self.app = app
        self.logger = logger or get_logger(conf, log_route="write_restriction")
        self.allowed_roles = list_from_csv(conf.get("allowed_roles", ""))
        self.write_methods = {"COPY", "POST", "PUT", "DELETE"}

    def __call__(self, env, start_response):
        req = Request(env)

        if req.method not in self.write_methods:
            return self.app(env, start_response)

        try:
            version, account, container, _ = req.split_path(3, 4, True)
            if not valid_api_version(version):
                raise ValueError
        except ValueError:
            return self.app(env, start_response)

        if req.method == "COPY" and "Destination" in req.headers:
            dest_container, _ = check_path_header(
                req,
                "Destination",
                2,
                "Destination header must be of the form <container name>/<object name>",
            )
            container = check_container_format(req, dest_container)

            if "Destination-Account" in req.headers:
                dest_account = wsgi_unquote(req.headers.get("Destination-Account"))
                account = check_account_format(req, dest_account)

        if not self.allowed_roles or not self.has_allowed_role(env):
            # We do not allow non-privileged users, i.e. users without any of the
            # allowed_roles, to set/update the 'X-Container-Meta-Write-Restricted' header.
            # This is to prevent them from locking themselves out of their containers.
            if (get_user_meta_prefix("container") + "write-restricted") in req.headers:
                msg = "User is not allowed to modify the write-restricted header."
                return HTTPMethodNotAllowed(body=msg)(env, start_response)

            if self.write_restricted_container(req, account, container):
                msg = "Writes are restricted for this container."
                return HTTPMethodNotAllowed(body=msg)(env, start_response)

        return self.app(env, start_response)

    def write_restricted_container(self, req, account, container):
        """
        Check whether a container is write restricted, i.e. the
        'X-Container-Meta-Write-Restricted' metadata header is set to 'true'.
        """
        info = get_info(self.app, req.environ, account, container, swift_source="WR")
        write_restricted = info.get("meta", {}).get("write-restricted", "")
        return config_true_value(write_restricted)

    def has_allowed_role(self, env):
        """
        Check whether the user that made the request has one of the allowed roles.
        """
        roles = list_from_csv(env.get("HTTP_X_ROLES", ""))
        service_roles = list_from_csv(env.get("HTTP_X_SERVICE_ROLES", ""))
        for r in self.allowed_roles:
            if r in roles or r in service_roles:
                return True

        return False


def filter_factory(global_conf, **local_conf):
    """
    Standard filter factory to use the middleware with paste.deploy.
    """
    conf = global_conf.copy()
    conf.update(local_conf)

    def write_restriction_filter(app):
        return WriteRestrictionMiddleware(app, conf)

    return write_restriction_filter
