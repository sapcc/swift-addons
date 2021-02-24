# Copyright 2021 SAP SE
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

from builtins import object
from swift.common.utils import get_logger

class InFlightCounterMiddleware(object):
    def __init__(self, app, conf):
        self.app = app
        self.logger = get_logger(conf, log_route='inflight_counter')

    @classmethod
    def factory(cls, global_config, **local_config):
        conf = global_config.copy()
        conf.update(local_config)
        def _factory(app):
            return cls(app, conf)
        return _factory

    def __call__(self, environ, start_response):
        # TODO increment connection counter
        try:
            # TODO remove debug code
            self.logger.info("Hello world!")
            if self.logger.statsd_client:
                self.logger.info("Hello world that contains statsd!")
            return self.app(environ, start_response)
        finally:
            pass # TODO decrement connection counter
