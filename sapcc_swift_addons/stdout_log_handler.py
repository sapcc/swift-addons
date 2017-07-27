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

class StdoutLogHandler(logging.Handler):
    def emit(self, record):
        six.print_(self.format(record))

def stdout_logger(conf, name, log_to_console, log_route, fmt, logger, adapted_logger):
    logger.addHandler(StdoutLogHandler())
