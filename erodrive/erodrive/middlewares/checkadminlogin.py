from erodrive import helpers
from django.http import HttpResponseRedirect
import hashlib
import time


class CheckAdminLogin:
    scope_uris = [
        '/admin/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path in self.scope_uris:
            admin_user = request.session.get('admin_auth_info')
            if not admin_user or not helpers.compare_admin_token(admin_user):
                return HttpResponseRedirect('/admin/login')

        return response


