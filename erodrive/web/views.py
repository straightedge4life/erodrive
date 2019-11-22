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
        'path_list': helpers.path_format(path)
    }

    return render(request, 'home/index.html', data)


def detail(request):
    file_path = request.GET.get('file_path')
    file_name = request.GET.get('file_name')
    suffix = file_name.split('.').pop()
    suffix_cat = None
    if not file_path or not file_name:
        return HttpResponseRedirect('/')
    one = OneDrive()
    file = one.get_file(path=file_path, name=file_name)
    show_configure = eval(helpers.config('show'))
    for conf in show_configure:
        if suffix in conf['suffix']:
            suffix_cat = conf['category']

    if suffix_cat == 'stream':
        text = requests.get(file['downloadUrl']).text
    data = {'file': file, 'suffix_cat': suffix_cat, 'text': text.encode('ascii', 'ignore')}
    if not suffix_cat:
        return HttpResponseRedirect('/?path='+file_path)

    return render(request, 'home/detail/'+suffix_cat+'.html', data)

