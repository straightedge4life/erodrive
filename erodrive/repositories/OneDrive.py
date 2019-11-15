from erodrive import helpers
import urllib
import requests
import json


class OneDrive:
    """
    One Drive repo class
    """
    __instance = None

    ru = "https://developer.microsoft.com/en-us/graph/quick-start?appID=_appId_&appName=_appName_&" \
         "redirectUrl=%s&platform=option-php"

    deep_link = "/quickstart/graphIO?publicClientSupport=false&appName=oneindex" \
                "&redirectUrl=%s&allowImplicitFlow=false&ru="

    app_url = "https://apps.dev.microsoft.com/?deepLink="

    api_url = "https://login.microsoftonline.com/common/oauth2/v2.0"

    scope = urllib.parse.quote('offline_access files.readwrite.all')

    def __new__(cls, *args, **kwargs):
        """
        Singleton mode
        :param args:
        :param kwargs:
        :return:
        """
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        return

    def get_app_url(self, redirect_url):
        """
        Generate application page url
        :param redirect_url:
        :return: string
        """
        ru = urllib.parse.quote(self.ru % redirect_url)
        deep_link = self.deep_link % redirect_url + ru
        return self.app_url + urllib.parse.quote(deep_link)

    def get_authorize_url(self):
        """
        Generate authorize url
        :return:
        """
        client_id = helpers.config('client_id')
        redirect_url = helpers.config('redirect_url')
        path = "/authorize?client_id=%s&scope=%s&response_type=code&redirect_uri=%s"
        return self.api_url + path % (client_id, self.scope, redirect_url)

    def get_token(self, code):
        """
        require token from Microsoft api by code
        :param code:
        :return:
        """
        url = self.api_url + "/token"
        headers = {
            'user-agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            'client_id': helpers.config('client_id'),
            'client_secret': helpers.config('client_secret'),
            'redirect_uri': helpers.config('redirect_url'),
            'code': code,
            'grant_type': 'authorization_code'
        }
        resp = json.loads(requests.post(url, payload, headers=headers).text)
        if resp.get('error'):
            raise Exception(resp.get('error_description'))
        helpers.batch_store_config(resp)
        return resp
