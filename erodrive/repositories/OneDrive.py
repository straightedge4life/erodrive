from erodrive import helpers
import urllib
import requests
import json
import os


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

    oauth_url = "https://login.microsoftonline.com/common/oauth2/v2.0"

    api_url = 'https://graph.microsoft.com/v1.0'

    scope = urllib.parse.quote('offline_access files.readwrite.all')

    # 4*1024*1024 = 4194304
    large_file_size = 4190000

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
        return self.oauth_url + path % (client_id, self.scope, redirect_url)

    def authorize(self, code):
        """
        require token from Microsoft api by code
        :param code:
        :return:
        """
        url = self.oauth_url + "/token"
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

        resp['is_install'] = True
        helpers.batch_store_config(resp)
        return resp

    def get_list(self, path: str = '/'):
        """
        获取文件列表
        :param path:
        :return:
        """

        if not path:
            path = '/'
        elif path != '/':
            path = urllib.parse.quote(':/' + path + ':/')

        query = 'children?select=name,size,folder,@microsoft.graph.downloadUrl,lastModifiedDateTime'
        url = self.api_url + '/me/drive/root' + path + query
        access_token = helpers.config('access_token')
        if not access_token:
            raise Exception('Access token does not exists.Please refresh token.')
        headers = {
            'Authorization': 'bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        resp = requests.get(url, headers=headers).text

        resp = json.loads(resp)

        if resp.get('error'):
            raise Exception(resp.get('error'))

        return resp

    def get_token(self):
        """
        Get access_token by refresh_token
        :return:
        """

        params = {
            'client_id': helpers.config('client_id'),
            'redirect_uri': helpers.config('redirect_url'),
            'client_secret': helpers.config('client_secret'),
            'refresh_token': helpers.config('refresh_token'),
            'grant_type': 'refresh_token'
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        url = self.oauth_url + '/token'

        resp = requests.post(url, data=params, headers=headers).text
        resp = json.loads(resp)

        if resp.get('error'):
            raise Exception(resp.get('error_description'))
        helpers.batch_store_config(resp)

        return None

    def get_file(self, path: str, name: str):
        """
        Find file in list
        :param path:
        :param name:
        :return:
        """
        file_list = self.get_list(path)['value']
        for f in file_list:
            if f['name'] == name:
                f.update({'downloadUrl': f.get('@microsoft.graph.downloadUrl')})
                del f['@microsoft.graph.downloadUrl']
                return f
        return []

    def upload(self, local_path: str, remote_path: str):
        # return bytes
        file_size = os.path.getsize(local_path)
        if file_size > self.large_file_size:
            return self.upload_large_file(local_path, remote_path, file_size)
        return self.upload_small_file(local_path, remote_path)

    def upload_small_file(self, local_path: str, remote_path: str):
        file_name = helpers.get_file_name(local_path)
        remote_path = self.prepare_remote_path(remote_path, file_name)
        access_token = helpers.config('access_token')

        if not access_token:
            raise Exception('Access token does not exists.Please refresh token.')

        headers = {
            'Authorization': 'bearer ' + access_token,
            'Content-Type': 'application/json'
        }

        with open(local_path, 'rb') as f:
            query = 'content'
            url = self.api_url + '/me/drive/root' + remote_path + query
            resp = requests.put(
                url,
                headers=headers,
                data=f
            ).text

        resp = json.loads(resp)
        if resp.get('error'):
            raise Exception(resp.get('error'))

        return resp

    def upload_large_file(self, local_path: str, remote_path: str, file_size: int):

        file_name = helpers.get_file_name(local_path)
        remote_path = self.prepare_remote_path(remote_path, file_name)
        access_token = helpers.config('access_token')

        if not access_token:
            raise Exception('Access token does not exists.Please refresh token.')

        headers = {
            'Authorization': 'bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        query = 'createUploadSession'
        url = self.api_url + '/me/drive/items' + remote_path + query
        # requests.post(
        #     url=url,
        #     headers=headers
        # )

        return None

    @staticmethod
    def prepare_remote_path(remote_path: str, file_name: str):
        if remote_path == '/' or not remote_path:
            remote_path = ''
        remote_path = urllib.parse.quote(':' + remote_path + '/' + file_name + ':/')
        return remote_path
