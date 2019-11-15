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
        redirect_url = 'https://www.straightedgelifestyles.club/redirect'

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
        'show': {
            'stream': ['txt'],
            'image': ['jpeg', 'jpg', 'png', 'gif'],
            'video': ['mp4', 'mkv', 'avi'],
            'audio': ['mp3', 'wav', 'ogg'],
        }
    }
    helpers.batch_store_config(data)
    one = OneDrive()
    oauth_url = one.get_authorize_url()
    return render(request, 'install/2.html', {'oauth_url': oauth_url})


def install_2(request, code):
    one = OneDrive()
    one.get_token(code)
    return JsonResponse({'status': 'SUCCESS'})
