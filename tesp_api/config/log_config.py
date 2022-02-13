import sys
import logging

from loguru import logger

from tesp_api.config.properties import properties


class InterceptLogHandler(logging.Handler):

    def emit(self, record):
        try:
            # Get corresponding Loguru level if it exists
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def get_subsequent_loggers(logger_name):
    segments = logger_name.split(".")
    return [".".join(segments[0:n + 1]) for n in range(len(segments))]


def logg_configure():
    intercept_handler = InterceptLogHandler()
    logging.root.setLevel(properties.logging.level)
    visited = set()

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    for name in [*logging.root.manager.loggerDict.keys(), "gunicorn", "gunicorn.access", "gunicorn.error", "uvicorn",
                 "uvicorn.access", "uvicorn.error"]:
        if name not in visited:
            for subsequent in get_subsequent_loggers(name):
                visited.add(subsequent)
            logging.getLogger(name).handlers = [intercept_handler]

    logger.configure(handlers=[{"sink": sys.stdout, "serialize": properties.logging.output_json}])
