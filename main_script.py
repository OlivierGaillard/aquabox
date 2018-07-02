from __future__ import print_function
import get_and_send_ph
import get_and_send_redox
import get_and_send_temperature
import shutdown
import time
import pijuice
import subprocess
import datetime
import os
import sys
import logging
from restclient import Sender

logname = '/home/pi/phweb/box/rest.log'
logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename=logname,
                    filemode='a', level=logging.DEBUG)


time.sleep(30)
get_and_send_ph.main()
time.sleep(10)
get_and_send_redox.main()
time.sleep(10)

shutdown.main()

