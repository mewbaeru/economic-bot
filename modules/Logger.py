import logging

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s:%(lineno)d]: %(message)s', datefmt='%d-%m-%y %H:%M:%S')

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_handler.setFormatter(formatter)

f_handler = logging.FileHandler('log.log', 'w', 'utf-8')
f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(formatter)

logger.addHandler(c_handler)
logger.addHandler(f_handler)