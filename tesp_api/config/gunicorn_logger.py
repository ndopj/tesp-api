import logging
from gunicorn.glogging import Logger

from tesp_api.config.properties import properties


class StubbedGunicornLogger(Logger):

    def __init__(self, cfg):
        super().__init__(cfg)
        self.error_logger = None
        self.access_logger = None

    def setup(self, cfg):
        handler = logging.NullHandler()
        self.error_logger = logging.getLogger("gunicorn.error")
        self.error_logger.addHandler(handler)
        self.access_logger = logging.getLogger("gunicorn.access")
        self.access_logger.addHandler(handler)
        self.error_logger.setLevel(properties.logging.level)
        self.access_logger.setLevel(properties.logging.level)
