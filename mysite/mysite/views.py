#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/28 下午4:15
# @Author  : Dlala
# @File    : views.py

from django.http import HttpResponse, Http404
import datetime
from django.shortcuts import render

def hello(request):
    return HttpResponse("Hello, World")


def current_datetime(request):
    now = datetime.datetime.now()
    return render(request, 'current_datetime.html', {'current_date': now})


def hours_ahead(request, offset):
    try:
        offset = int(offset)
    except ValueError:
        raise Http404()
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    html = "In %s hours, it will be %s." % (offset, dt)
    return HttpResponse(html)
