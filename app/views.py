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
    lastDate = datetime.fromtimestamp(float(timestamp)/1000)
    now = datetime.now()
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
            'image': host + adv.pic.url,
            'priority': adv.news_priority,
            'pubDate': adv.pub_date,
        }
        ret_list.append(attr_dic)
    return JsonResponse(ret_list,safe=False)
def get_recom(request):
    adv_list = list(Advertisement.objects.filter(location__in=['0','1'],is_hidden=False)[0:5])
    first_adv = adv_list[0] if adv_list else None
    last_adv = adv_list[-1] if adv_list else None
    now = datetime.now()
    start = now - timedelta(days=1)
    adv_today1 = MAdvert.objects.filter(location='1',is_hidden=False).first()
    adv_today2 = MAdvert.objects.filter(location='2',is_hidden=False).first()
    adv_today3 = MAdvert.objects.filter(location='3',is_hidden=False).first()
    adv_today1_info = {'pic_url':adv_today1.pic.url, 'url':adv_today1.url}
    adv_today2_info = {'pic_url':adv_today2.pic.url, 'url':adv_today2.url}
    adv_today3_info = {'pic_url':adv_today3.pic.url, 'url':adv_today3.url}
    adv_info_list = []
    for adv in adv_list:
        dic = {}
        dic['pic_url'] = host + str(adv.mpic.url)
        dic['url'] = adv.url
        adv_info_list.append(dic)
    context = {'adv_info_list':adv_info_list,
               'adv_today1_info':adv_today1_info,
               'adv_today2_info':adv_today2_info,
               'adv_today3_info':adv_today3_info,
    }
    try:
        statis = DayStatis.objects.get(date=date.today())
    except:
        new_wel_num = 0
    else:
        new_wel_num = statis.new_wel_num
    glo_statis = GlobalStatis.objects.first()
    if glo_statis:
        all_wel_num = glo_statis.all_wel_num
        withdraw_total = glo_statis.award_total
        
    else:
        withdraw_total = 0
        all_wel_num = 0
    context.update({'new_wel_num':new_wel_num, 'all_wel_num':all_wel_num, 'withdraw_total':withdraw_total})
    return JsonResponse(context)
