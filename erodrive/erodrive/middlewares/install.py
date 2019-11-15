from erodrive import helpers
from django.http import HttpResponseRedirect


class InstallMiddleware:
    except_uris = [
        '/admin/install'
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Code will be execute here.
        if not helpers.config('is_install') and request.path not in self.except_uris:
            return HttpResponseRedirect('admin/install')
        return response
