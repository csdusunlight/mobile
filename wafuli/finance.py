#coding:utf-8
from django.shortcuts import render
from django.http.response import Http404
from wafuli.models import Finance, Advertisement
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.db.models import F,Q
import logging
from wafuli.tools import update_view_count
from django.contrib.auth.decorators import login_required
logger = logging.getLogger('wafuli')
from .tools import listing
import re
from itertools import chain
from datetime import datetime, timedelta


def finance(request, id=None):
    if id is None:
        adv_list = list(Advertisement_Mobile.objects.filter(location__in=['0','4'],is_hidden=False)[0:1])
        first_adv = adv_list[0] if adv_list else None
        last_adv = adv_list[-1] if adv_list else None
#         hot_wel_list = Welfare.objects.filter(is_display=True,state='1').order_by('-view_count')[0:3]
        context = {'adv_list':adv_list, 'first_adv':first_adv, 'last_adv':last_adv,}
        return render(request, 'm_finance.html', context)
    else:
        id = int(id)
        news = None
        try:
            news = Finance.objects.get(id=id)
        except Finance.DoesNotExist:
            raise Http404(u"该页面不存在")
        update_view_count(news)
        scheme = news.scheme
        table = []
        str_rows = scheme.split('|')
        for str_row in str_rows:
            row = str_row.split('#')
            table.append(row);
        context = {
                   'news':news,
                   'type':'Finance',
                   'table':table,
        }
        ref_url = request.META.get('HTTP_REFERER',"")
        if 'next=' in ref_url:
            context.update({'back':True})
        return render(request, 'm_detail_finance.html',context)

def add_finance(request, id=None):
    if id is None:
        adv_list = list(Advertisement_Mobile.objects.filter(location__in=['0','4'],is_hidden=False)[1:2])
        first_adv = adv_list[0] if adv_list else None
        last_adv = adv_list[-1] if adv_list else None
#         hot_wel_list = Welfare.objects.filter(is_display=True,state='1').order_by('-view_count')[0:3]
        context = {'adv_list':adv_list, 'first_adv':first_adv, 'last_adv':last_adv,}
        return render(request, 'm_finance.html', context)
    else:
        id = int(id)
        news = None
        try:
            news = Finance.objects.get(id=id)
        except Finance.DoesNotExist:
            raise Http404(u"该页面不存在")
        update_view_count(news)
        scheme = news.scheme
        table = []
        str_rows = scheme.split('|')
        for str_row in str_rows:
            row = str_row.split('#')
            table.append(row);
        context = {
                   'news':news,
                   'type':'Finance',
                   'table':table,
        }
        ref_url = request.META.get('HTTP_REFERER',"")
        if 'next=' in ref_url:
            context.update({'back':True})
        return render(request, 'm_detail_finance.html',context)


def get_finance_page(request):
    res={'code':0,}
    page = request.GET.get("page", None)
    size = request.GET.get("size", 5)
    filter = request.GET.get("filter", 0)
    state = request.GET.get("state", 0)
    try:
        size = int(size)
    except ValueError:
        size = 6
    if not page or size <= 0:
        raise Http404
    item_list = Finance.objects.all()
    filter = str(filter)
    state = str(state)
    if filter != '0':
        item_list = item_list.filter(filter=filter)
    item_list = item_list.filter(state=state)
    paginator = Paginator(item_list, size)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    data = []
    for con in contacts:
        i = {"title":con.title,
             "interest":con.interest,
             "amount":con.amount_to_invest,
             "time":con.investTime,
             "scores":con.scrores,
             "benefit":con.benefit,
             "url":con.url,
             "is_new":'new' if con.is_new() else '',
        }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)
