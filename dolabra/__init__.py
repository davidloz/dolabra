import logging

from mythril.mythril.mythril_config import MythrilConfig

#__version__ = '0.2.7'

formatter = logging.Formatter('[%(levelname)s\t] %(asctime)s - %(name)s %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

log = logging.getLogger(__name__)
log.addHandler(stream_handler)
log.setLevel(logging.INFO)

MythrilConfig()

