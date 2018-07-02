"""
Sensor box settings for piscinewatch project.

The file contains the informations needed to access the REST service.

This file should be renamed to 'boxsettings.py'
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


REST_SERVICE   = 'http://aquawatch.ch'

#REST_SERVICE2   = 'http://192.168.0.16:8000'
REST_USER     =  'your user name'
REST_PASSWORD =  'your password'

FAKE_DATA = True

USB_PORT = '/dev/ttyAMA0'

SHUT_DOWN = False

