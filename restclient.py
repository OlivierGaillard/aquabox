import requests
import boxsettings
import logging


class Sender:
    """The class responsible for sending data to the REST service."""

    def __init__(self):
        self.live_server_url = boxsettings.REST_SERVICE
        self.user_box = boxsettings.REST_USER
        self.user_box_passwd = boxsettings.REST_PASSWORD
        self.logger = logging.getLogger(__name__)
        self.online = False
        try:
            r = requests.get(self.live_server_url)
            if r.status_code == 200:
                self.online = True
                self.logger.debug('Sender can reach %s' % self.live_server_url)
            else:
                self.logger.debug('Sender is online but cannot reach %s' % self.live_server_url)
        except:
            self.logger.debug('Sender cannot reach %s' % self.live_server_url)

    def is_online(self):
        return self.online


    def __send_data(self, json, urlsuffix):
        url = self.live_server_url + urlsuffix
        self.logger.debug('REST url: %s' % url)
        self.logger.debug('JSON: %s'     % json)
        self.logger.debug('User: %s'     % self.user_box)
        r = requests.post(url, json=json, auth=(self.user_box, self.user_box_passwd))
        if r.status_code != 201:
            self.logger.fatal("Cannot reach REST service: %s", url)
        else:
            self.logger.info("Data sent to %s of REST service.", urlsuffix)
        return r

    def send_deg(self, value):
        """A relever: la cle json 'celsius' est identique au champ de la table
        'Deg'. """
        value_str = '%.3f' % value
        json = {'celsius': value_str}
        return self.__send_data(json, '/deg/')


    def __del_data(self, id, data_type):
        url = self.live_server_url + '/%s/%s/delete/' % (data_type, id)
        r = requests.post(url, auth=(self.user_box, self.user_box_passwd))
        if r.status_code != 201:
            self.logger.fatal("Cannot reach REST service.")
            return r.status_code
        else:
            self.logger.info("Deleted data %s with ID %s" % (data_type, id))
            return r.status_code

    def del_deg(self, id):
        return self.__del_data(id, 'deg')


    def send_ph(self, value):
        value_str = '%.3f' % value
        json = {'phval': value_str}
        return self.__send_data(json, '/ph/')

    def send_redox(self, value):
        value_str = '%.1f' % value
        json = {'redoxval': value_str}
        return self.__send_data(json, '/redox/')

    def __get_last(self, data_type):
        measures = {'deg' : 'celsius', 'ph' : 'phval', 'redox' : 'redoxval'}
        url_suffix = '/%s/last/' % data_type
        url = self.live_server_url + url_suffix
        r = requests.get(url, auth=(self.user_box, self.user_box_passwd))
        if r.status_code != 200:
            self.logger.fatal("Cannot reach REST service.")
            self.logger.info("Error: %s" % r.status_code)
            return r
        else:
            value = r.json()[measures[data_type]]
            self.logger.info("Last value stored: %s" % value)
            return r


    def deg_last(self):
        return self.__get_last('deg')

    def get_pool_settings(self):
        url = self.live_server_url + '/piscine/'
        r = requests.get(url, auth=(self.user_box, self.user_box_passwd))
        if r.status_code != 200:
            self.logger.fatal("Cannot reach REST service.")
            self.logger.info("Error: %s" % r.status_code)
            raise Exception("Connection to REST service failed.")
        else:
            values = r.json()
            return values

    # def get_shutdown_settings(self):
    #     enable_shutdown = None
    #     try:
    #         values = self.get_pool_settings() # Json object
    #         enable_shutdown = values['enable_shutdown']
    #         self.logger.info("Making a shutdown or not? Answer: %s" % enable_shutdown)
    #     except:
    #         pass
    #     return enable_shutdown
    #
    # def get_update_settings(self):
    #     do_update = None
    #     try:
    #         values = self.get_pool_settings() # Json object
    #         do_update = values['do_update']
    #         self.logger.info("Making update or not? Answer: %s" % do_update)
    #     except:
    #         pass
    #     return do_update

    def send_battery_level(self, value):
        value_str = '%s' % value
        json = {'battery_charge': value_str}
        return self.__send_data(json, '/battery/')

    def send_log(self, log_text):
        json = {'log': log_text}
        return self.__send_data(json, '/log/')


if __name__ == '__main__':
    sender = Sender()
