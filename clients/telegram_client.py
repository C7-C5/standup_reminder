import requests


class TelegramClient:
    def __init__(self, token, base_url):
        self.__token = token
        self.__base_url = base_url

    def prepare_url(self, method):
        """
        constructs urls for requests
        """
        final_url = f'{self.__base_url}/bot{self.__token}/'
        if method is not None:
            final_url += method
        return final_url

    def post(self, method, params=None, body=None):
        """
        sends generated request by POST-method, returns response
        """
        url = self.prepare_url(method)
        response = requests.post(url=url, params=params, data=body)
        return response.json()

