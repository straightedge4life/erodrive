from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from erodrive import helpers
from repositories.OneDrive import OneDrive


def index(request):
    one = OneDrive()
    item_list = one.get_list()
    data = {
        'item_list': one.get_list()['value']
    }
    return render(request, 'home/index.html', data)


