from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from erodrive import helpers
from repositories.OneDrive import OneDrive
import requests


def index(request):
    """
    List page in frontend
    :param request:
    :return:
    """
    one = OneDrive()
    path = request.GET.get('path', '/')
    item_list = helpers.list_format(one.get_list(path)['value'])

    data = {
        'item_list': item_list,
        'curr_path': '' if path == '/' else path,
        'path_list': helpers.path_format(path),
        'site_name': helpers.config('site_name'),
    }

    return render(request, 'home/index.html', data)


def detail(request):
    """
    Detail page to show the file type can show/play on website.
    :param request:
    :return:
    """
    file_path = request.GET.get('file_path', '/')
    file_name = request.GET.get('file_name')
    suffix = file_name.split('.').pop()
    suffix_cat = None
    if not file_name:
        return HttpResponseRedirect('/')
    one = OneDrive()

    file = one.get_file(path=file_path, name=file_name)
    if not file:
        return HttpResponseRedirect('/')

    show_configure = eval(helpers.config('show'))
    for conf in show_configure:
        if suffix in conf['suffix']:
            suffix_cat = conf['category']

    data = {
        'file': file,
        'suffix_cat': suffix_cat,
        'site_name': helpers.config('site_name'),
        'file_name': file_name,
    }
    if suffix_cat == 'stream':
        data.update({'text': requests.get(file['downloadUrl']).text.encode('ascii', 'ignore')})

    if not suffix_cat:
        return HttpResponseRedirect('/?path='+file_path)

    return render(request, 'home/detail/'+suffix_cat+'.html', data)


def login(request):
    """
    Login Page(if set access code)
    :param request:
    :return:
    """

    if request.method == 'POST':
        access_token = helpers.config('access_code')
        if request.POST.get('access_code') != access_token:
            return HttpResponseRedirect('/login')
        else:
            token, timestamp = helpers.generate_token(val=access_token)
            request.session['auth_info'] = {
                'token': token,
                'time': timestamp
            }
            return HttpResponseRedirect('/')
    data = {
        'site_name': helpers.config('site_name')
    }

    return render(request, 'home/login.html', data)
