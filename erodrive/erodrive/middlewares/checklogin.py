from erodrive import helpers
from django.http import HttpResponseRedirect
import hashlib
import time


class CheckLogin:
    scope_uris = [
        '/',
        '/detail'
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        access_code = helpers.config('access_code')
        if request.path in self.scope_uris and access_code:
            auth_info = request.session.get('auth_info')
            if not auth_info or not helpers.compare_web_token(auth_info):
                return HttpResponseRedirect('/login')

        return response


