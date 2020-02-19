import logging


def logger(name=None):
    logging.basicConfig(filename='tracker.log', format='%(asctime)s %(message)s')
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    return log