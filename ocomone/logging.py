"""Copyright 2019 Anton Kachurin

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler


def setup_logger(logger: logging.Logger, log_name: str = None,
                 log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                 log_dir="./logs"):
    """Setup logger with ``INFO`` level stream output + ``DEBUG`` level rotating file log

    :param logger: logger to be wrapped. Do not wrap same logger twice!
    :param log_name: name of logfile to be created
    :param log_format: format of log output
    :param log_dir: path to rotating file log directory
    """
    formatter = logging.Formatter(log_format)
    if log_name is None:
        log_name = logger.name.lower()
    try:
        # debug+ messages goes to log file
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        f_hdl = TimedRotatingFileHandler(f"{log_dir}/{log_name}.log", backupCount=10, when="midnight", utc=True)
        f_hdl.setLevel(logging.DEBUG)
        f_hdl.setFormatter(formatter)
        logger.addHandler(f_hdl)
    except OSError:
        pass
    # info+ messages goes to stream
    s_hdl = logging.StreamHandler()
    s_hdl.setLevel(logging.INFO)
    s_hdl.setFormatter(formatter)
    logger.addHandler(s_hdl)
