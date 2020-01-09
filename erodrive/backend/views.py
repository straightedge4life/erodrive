from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from erodrive import helpers
from repositories.OneDrive import OneDrive


def install(request):
    """
    Installation headquarter function
    :param request:
    :return:
    """
    # be careful data-type is string from request query string
    step = request.GET.get('step', '0')
    code = request.GET.get('code', None)

    if code:
        return install_2(request, code)

    func_name = 'install_'+step
    return globals()[func_name](request)


def install_0(request):
    """
    1.Generate application page url
    2.Guide user copy client id an client secret from app page and submit.
    :param request:
    :return:
    """
    host = request.get_host().split(':', -1)[0]
    if host == 'localhost':
        redirect_url = 'http://localhost:8000/admin/install'
    else:
        redirect_url = 'https://redirect.seniordriver.top'

    one = OneDrive()
    url = one.get_app_url(redirect_url)
    data = {
        'url': url,
        'redirect_url': redirect_url
    }

    return render(request, 'install/1.html', data)


def install_1(request):
    """
    1.Receive param from previous step,and validate it.
    2.Write into config file.
    3.Use this param to generate oauth url.
    :param request:
    :return:
    """
    params = request.POST
    if not params:
        return HttpResponseRedirect('/admin/install')
    # write into configure file

    data = {
        'client_id': params.get('client_id', ''),
        'client_secret': params.get('client_secret', ''),
        'redirect_url': params.get('redirect_url', ''),
        'show': [
            {'category': 'stream', 'suffix': ['txt']},
            {'category': 'image', 'suffix': ['jpeg', 'jpg', 'png', 'gif']},
            {'category': 'video', 'suffix': ['mp4', 'mkv', 'avi']},
            {'category': 'audio', 'suffix': ['mp3', 'wav', 'ogg']}
        ],
        'site_name': 'ERO DRIVE',
        'password': 'shikoeveryday',
        'access_code': '',
        'salt': helpers.rand_str(32)
    }
    helpers.batch_store_config(data)
    one = OneDrive()
    curr_url = None
    curr_host = request.get_host().split(':', -1)[0]
    if curr_host == 'localhost':
        http_referrer = request.get_raw_uri().split(':', -1)[0] + '://'
        curr_url = http_referrer + request.get_host() + '/admin/install'
    oauth_url = one.get_authorize_url()

    if curr_host == 'localhost':
        return render(request, 'install/2-local.html', {'oauth_url': oauth_url})
    else:
        return render(request, 'install/2.html', {'oauth_url': oauth_url})


def install_2(request, code):
    """
    Go authorize then writen in configure file
    :param request:
    :param code:
    :return:
    """
    one = OneDrive()
    one.authorize(code)
    http_referrer = request.get_raw_uri().split(':', -1)[0] + '://'
    host = http_referrer + request.get_host()
    data = {
        'host': host,
        'password': helpers.config('password'),
        'site_name': helpers.config('site_name'),
    }
    return render(request, 'install/success.html', data)


def index(request):
    if request.POST:
        helpers.batch_store_config({
            'site_name': request.POST.get('site_name', 'ERO DRIVE'),
            'password': request.POST.get('password'),
            'access_code': request.POST.get('access_code'),
        })

    configure = {
        'site_name': helpers.config('site_name'),
        'password': helpers.config('password'),
        'access_code': helpers.config('access_code'),
    }
    return render(request, 'adm/index.html', configure)


def login(request):
    """
    Login page & method
    :param request:
    :return:
    """
    if request.POST:
        c_password = str(request.POST.get('password'))
        if c_password != str(helpers.config('password')):
            return HttpResponseRedirect('/admin/login')

        token, timestamp = helpers.generate_token(val=c_password)
        request.session['admin_auth_info'] = {
            'token': token,
            'time': timestamp
        }
        return HttpResponseRedirect('/admin')

    data = {
        'site_name': helpers.config('site_name')
    }
    return render(request, 'adm/login.html', data)
