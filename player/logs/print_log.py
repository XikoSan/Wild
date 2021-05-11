import logging


# замена print в Докере
def log(object):
    logger = logging.getLogger(__name__)
    logger.info(object)
