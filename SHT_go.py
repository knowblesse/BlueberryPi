from pi_sht1x import SHT1x
import RPi.GPIO as GPIO
import time
import logging

#constants
rf_time_in_min = 0.2

#Logging Setup
FORMAT = '%(asctime)s %(levelno)s %(message)s'
LOG_NAME = str(time.localtime().tm_year) +'-'+ str(time.localtime().tm_mon) + '-' + str(time.localtime().tm_mday)
logging.basicConfig(filename=LOG_NAME+'_debug', level=logging.INFO, format=FORMAT)

class ContextFilter(logging.Filter):
    def filter(self, record):
        if record.levelname=='WARNING':
            return True
        else:
            return False

logger = logging.getLogger('Logger')
fmt = logging.FileHandler(LOG_NAME)
fmt.setFormatter(logging.Formatter(fmt=FORMAT))
logger.addHandler(fmt)
logger.addFilter(ContextFilter())

sensor = SHT1x(18,23,gpio_mode=GPIO.BCM)

init_time = time.time()

while(True):
        if(time.time() - init_time > rf_time_in_min*60):
            msg = str(time.ctime()) + ' ~ {0:.2f}C  |  {1:.2f}%'.format(sensor.read_temperature(), sensor.read_humidity())
            print(msg)
            logger.warning('{0:.2f}C | {1:.2f}%'.format(sensor.read_temperature(), sensor.read_humidity()))           
            init_time = time.time()

    

