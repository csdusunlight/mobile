from django.shortcuts import render
from wafuli.models import Advertisement, Welfare, MAdvert
from wafuli_admin.models import DayStatis
from datetime import datetime, timedelta, date
from wafuli_admin.models import GlobalStatis
from django.http.response import JsonResponse
host = 'http://m.wafuli.cn'
def get_news(request):
    timestamp = request.GET.get('lastDate','')
    if not timestamp:
        return JsonResponse('',safe=False)
    lastDate = None
    try:
        lastDate = datetime.fromtimestamp(float(timestamp)/1000)
    except:
        lastDate = datetime.now()
    last_wel_list = Welfare.objects.filter(is_display=True,state='1',startTime__lte=lastDate).\
        exclude(type='baoyou').order_by("-startTime")[0:10]
    ret_list = []
    for wel in last_wel_list:
        marks = wel.marks.all()
        markc = len(marks)
        attr_dic = {
            'id':wel.id,
            'title':wel.title,
            'mark1': marks[0].name if markc > 0 else '',
            'mark2': marks[1].name if markc > 1 else '',
            'mark3': marks[2].name if markc > 2 else '',
            'pubDate': wel.startTime.strftime('%m-%d-%Y %H:%M:%S'),
            'image': host + wel.pic.url,
            'time': wel.time_limit,
            'source': wel.provider,
            'view': wel.view_count
        }
        ret_list.append(attr_dic)
    return JsonResponse(ret_list,safe=False)
def get_slider(request):
    adv_list = list(Advertisement.objects.filter(location__in=['0','1'],is_hidden=False)[0:5])
    ret_list = []
    for adv in adv_list:
        attr_dic = {
            'id':adv.id,
            'image': host + adv.mpic.url,
            'priority': adv.news_priority,
            'pubDate': adv.pub_date,
        }
        ret_list.append(attr_dic)
    return JsonResponse(ret_list,safe=False)
def get_recom(request):
    adv_today1 = MAdvert.objects.filter(location='1',is_hidden=False).first()
    adv_today2 = MAdvert.objects.filter(location='2',is_hidden=False).first()
    adv_today3 = MAdvert.objects.filter(location='3',is_hidden=False).first()
    ret_list = [{
        'id':adv_today1.id,
        'image': host + adv_today1.pic.url,
        'location': 1,
    },{
        'id':adv_today2.id,
        'image': host + adv_today2.pic.url,
        'location': 2,
    },{
        'id':adv_today3.id,
        'image': host + adv_today3.pic.url,
        'location': 3,
    }]
    return JsonResponse(ret_list,safe=False)