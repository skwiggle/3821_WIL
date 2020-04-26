import asyncio
import logging
import sys
from datetime import datetime as dt

logging.basicConfig(
    filemode='a+',
    filename='test.txt',
    format='%(asctime)s: %(message)s'
)
logger = logging.getLogger('testLogger')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

logger.critical(msg='This is a test')



