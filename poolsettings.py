import json
import logging
from restclient import Sender

logname = '/home/pi/phweb/box/rest.log'
logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename=logname,
                    filemode='a', level=logging.INFO)

class PoolSettings:
    """Encapsulates pool settings like:
    - shutdown enable
    - next wakeup
    - do update
    """

    # In case of no connection we load the previously saved JSON-settings
    # If no JSON file can be found we define fall-back values here
    settings = {'enable_reading' : False, 'do_update' : False,
                'time_between_readings' : 24, 'enable_shutdown' : False}

    file_name = "settings.json"
    online = False

    def __init__(self):
        sender = Sender()
        settings_json = None
        try:
            settings_json = sender.get_pool_settings()
            self.settings = settings_json[0]
            logging.info('Saving settings to local JSON file %s ' % self.file_name)
            with open(self.file_name, 'w') as outfile:
                json.dump(self.settings, outfile)
            logging.info("Settings written to file.")
            self.online = True
        except:
            logging.warning('Connection error.')


        finally:
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

    def time_beetween_readings(self):
        return self.settings['time_beetween_readings']

    def enable_reading(self):
        return self.settings['enable_reading']