import json
import logging
from restclient import Sender


class PoolSettings:
    """Encapsulates pool settings like:
    - shutdown enable
    - next wakeup
    - do update
    """


    # In case of no connection we load the previously saved JSON-settings
    # If no JSON file can be found we define fall-back values here
    settings = {'enable_reading' : False, 'do_update' : False,
                'time_between_readings' : 24, 'enable_shutdown' : False,
                'log_level' : logging.DEBUG}

    file_name = "settings.json"
    online = False

    def __init__(self):
        sender = Sender()
        try:
            settings_json = sender.get_pool_settings()
            self.settings = settings_json[0]
            logging.info('We are online.\n Saving settings to local JSON file %s ' % self.file_name)
            with open(self.file_name, 'w') as outfile:
                json.dump(self.settings, outfile)
            logging.info("Settings written to file.")
            self.online = True
        except:
            logging.warning('Connection error.')
            logging.warning("trying to load previous settings from file, as network connection fails.")
            file_name = 'settings.json'
            try:
                with open(file_name) as infile:
                    self.settings = json.load(infile)
                logging.info("Success reading from file")
            except:
                # falling back to default
                logging.warning("No file found. Using default values")

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


class HoursUtils:
    "Utility to get starting hour and next hour of readings based on the current UTC time."

    UTC_DELTA = -2
    hours = []
    next_hour = 0
    current_hour = 0

    def __init__(self, hours_enum, current_hour):
        """
        :param hours_enum: 8,12,18
        :return: [8,12,18]
        """
        self.hours = [int(h)+self.UTC_DELTA for h in hours_enum.split(',')]
        self.current_hour = current_hour
        self.__set_next_hour()

    def __set_next_hour(self):
        next_h = 0
        for n in self.hours:
            if self.current_hour < n:
                next_h = n
                break
        if next_h == 0:
            next_h = self.hours[0]
        self.next_hour = next_h


    def next_reading_hour(self):
        """

        :param h: current hour
        :return: next reading hour
        """
        return  self.next_hour

    def next_reading_hour_local(self):
        return self.next_hour - self.UTC_DELTA



