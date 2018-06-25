import requests
import boxsettings
import logging

logname = 'rest.log'
logging.basicConfig(format='%(levelname)s\t: %(asctime)s : %(message)s', filename=logname,
                    filemode='a', level=logging.INFO)


class Sender:
    """The class responsible for sending data to the REST service."""

    def __init__(self):
        self.live_server_url = boxsettings.REST_SERVICE
        self.user_box = boxsettings.REST_USER
        self.user_box_passwd = boxsettings.REST_PASSWORD

    def __send_data2(self, json, server_url, urlsuffix):
        url = server_url + urlsuffix
        r = requests.post(url, json=json, auth=(self.user_box, self.user_box_passwd))
        if r.status_code != 201:
            logging.fatal("Cannot reach REST service %s", url)
        else:
            logging.info("Data sent to %s of REST service.", urlsuffix)
        return r


    def __send_data(self, json, urlsuffix):
        url = self.live_server_url + urlsuffix
        r = requests.post(url, json=json, auth=(self.user_box, self.user_box_passwd))
        if r.status_code != 201:
            logging.fatal("Cannot reach REST service: %s", url)
        else:
            logging.info("Data sent to %s of REST service.", urlsuffix)
        return r

    def send_deg(self, value):
        """A relever: la cle json 'celsius' est identique au champ de la table
        'Deg'. """
        value_str = "{0:.3f}".format(value)
        json = {'celsius': value_str}
        url = self.live_server_url + '/deg/'
        return self.__send_data(json, '/deg/')



    def __del_data(self, id, data_type):
        url = self.live_server_url + '/%s/%s/delete/' % (data_type, id)
        r = requests.post(url, auth=(self.user_box, self.user_box_passwd))
        if r.status_code != 201:
            logging.fatal("Cannot reach REST service.")
            return r.status_code
        else:
            logging.info("Deleted data %s with ID %s" (data_type, id))
            return r.status_code

    def del_deg(self, id):
        return self.__del_data(id, 'deg')


    def send_ph(self, value):
        value_str = "{0:.3f}".format(value)
        json = {'phval': value_str}
        url = self.live_server_url + '/ph/'
        return self.__send_data(json, '/ph/')

    def send_redox(self, value):
        value_str = "{0:.1f}".format(value)
        json = {'redoxval': value_str}
        url = self.live_server_url + '/redox/'
        return self.__send_data(json, '/redox/')

    def __get_last(self, data_type):
        measures = {'deg' : 'celsius', 'ph' : 'phval', 'redox' : 'redoxval'}
        url_suffix = '/%s/last/' % data_type
        url = self.live_server_url + url_suffix
        r = requests.get(url, auth=(self.user_box, self.user_box_passwd))
        if r.status_code != 200:
            logging.fatal("Cannot reach REST service.")
            return r
        else:
            value = r.json()[measures[data_type]]
            logging.info("Last value stored: %s" % value)
            return r


    def deg_last(self):
        return self.__get_last('deg')



if __name__ == '__main__':
    sender = Sender()
