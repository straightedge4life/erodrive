from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from erodrive import helpers
from repositories.OneDrive import OneDrive


def index(request):
    one = OneDrive()
    path = request.GET.get('path', '/')
    item_list = helpers.list_format(one.get_list(path)['value'])

    data = {
        'item_list': item_list,
        'curr_path': '' if path == '/' else path,
        'path_list': path_format(path)
    }

    return render(request, 'home/index.html', data)


def path_format(path):
    if not path or path == '/':
        return [{'name': '/', 'path': '/'}]
    path_chain = ''
    path_list = []
    for p in path.split('/'):
        name = p if p else '/'
        if path_chain == '/':
            path_chain = path_chain + p
        else:
            path_chain = path_chain + '/' + p

        path_list.append({
            'name': name,
            'path': path_chain
        })
    return path_list
