from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from erodrive import helpers


def index(request):
    resp = {
        'name_space': 'web.index'
    }
    return JsonResponse(resp)


