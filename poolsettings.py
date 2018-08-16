import json
import logging
import datetime
from restclient import Sender



class PoolSettings:
    """Encapsulates pool settings like:
    - shutdown enable
    - next wakeup
    - do update
    """


    # In case of no connection we load the previously saved JSON-settings
    # If no JSON file can be found we define fall-back values here

    file_name = "settings.json"


    def __init__(self):
        self.logger = logging.getLogger('PoolSettings')
        self.settings = {'enable_reading': False, 'do_update': False,
                    'time_between_readings': 24, 'enable_shutdown': False,
                    'log_level': logging.DEBUG, 'bigshutdown' : False}

        self.online = False
        sender = Sender()

        try:
            settings_json = sender.get_pool_settings()
            self.settings = settings_json[0]
            self.logger.info('We are online. Saving settings to local JSON file %s ' % self.file_name)
            with open(self.file_name, 'w') as outfile:
                json.dump(self.settings, outfile)
            self.logger.info("Settings written to file.")
            self.online = True
        except Exception, e:
            self.logger.warning('Connection error.', exc_info=True)
            self.logger.info("trying to load previous settings from file, as network connection fails.")
            file_name = 'settings.json'
            try:
                with open(file_name) as infile:
                    self.settings = json.load(infile)
                self.logger.info("Success reading from file")
            except Exception, e:
                # falling back to default
                self.logger.warning("No file found. Using default values", exc_info=True)


    def is_online(self):
        return self.online

    def enable_shutdown(self):
        enable_shutdown = self.settings['enable_shutdown']
        return enable_shutdown

    def do_update(self):
        return self.settings['do_update']

    def enable_reading(self):
        return self.settings['enable_reading']

    def hours_of_readings(self):
        return self.settings['hours_of_readings']

    def log_level(self):
        return self.settings['log_level']

    def bigshutdown(self):
        return self.settings['bigshutdown']


class HoursUtils:
    "Utility to get starting hour and next hour of readings based on the current UTC time."

    UTC_DELTA = -2
    hours = []
    next_hour = 0
    current_hour = 0

    def __init__(self, hours_enum):
        """
        :param hours_enum: 8,12,18
        :return: [8,12,18]
        """
        self.logger = logging.getLogger('HoursUtils')
        self.hours = [int(h)+self.UTC_DELTA for h in hours_enum.split(',')]
        self.logger.debug('Reading hours: %s' % self.hours)
        self.current_hour = datetime.datetime.utcnow()
        self.__set_next_hour()

    def __set_next_hour(self):
        next_h = 0
        for n in self.hours:
            if self.current_hour.hour < n:
                next_h = n
                break
        if next_h == 0:
            next_h = self.hours[0]
        self.next_hour = next_h
        self.logger.debug('Next reading hour UTC: %s', self.next_hour)


    def next_reading_hour(self):
        """

        :param h: current hour
        :return: next reading hour
        """
        return  self.next_hour

    def next_reading_hour_local(self):
        return self.next_hour - self.UTC_DELTA



