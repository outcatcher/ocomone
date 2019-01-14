"""Common function implementations"""
import logging
import os
from logging.handlers import TimedRotatingFileHandler


class Resources:
    """Resource retrieval from dedicated resource directory.

    Example:
        ``resources = Resources(__file__)``

        ``resources["my_file.txt"]``

            will have return of:

        ``C:\\\\Path\\to\\python_file\\resources\\my_file.txt``
    """

    def __init__(self, content_root: str, resources_dir: str = "resources"):
        """Initialize resource retrieval, normally `content_root` should be `__file__`"""
        self.resource_root = os.path.abspath(f"{os.path.dirname(content_root)}/{resources_dir}")

    def __getitem__(self, resource_name):
        """Return path to resource by given name. If given path is absolute, return if without change"""
        if os.path.isabs(resource_name):
            return resource_name
        return os.path.abspath(f"{self.resource_root}/{resource_name}")


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
