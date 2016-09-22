#coding:utf-8
from django.shortcuts import render
from django.http.response import Http404
from wafuli.models import Welfare, Task, Finance, Commodity, Information, \
    ExchangeRecord, Press, UserEvent, Advertisement, Activity, Company,\
    CouponProject, Baoyou, Hongbao, MAdvert
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from account.transaction import charge_score
import logging
from datetime import date
from wafuli_admin.models import DayStatis, GlobalStatis, RecommendRank
from account.models import MyUser
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
logger = logging.getLogger('wafuli')
from .tools import listing, update_view_count
import re

def index(request):
    adv_list = list(Advertisement.objects.filter(location__in=['0','1'],is_hidden=False)[0:8])
    first_adv = adv_list[0] if adv_list else None
    last_adv = adv_list[-1] if adv_list else None
    last_wel_list = Welfare.objects.filter(is_display=True,state='1').order_by("-startTime")[0:3]
    adv_today1 = MAdvert.objects.filter(location='1',is_hidden=False).first()
    adv_today2 = MAdvert.objects.filter(location='2',is_hidden=False).first()
    adv_today3 = MAdvert.objects.filter(location='3',is_hidden=False).first()
    context = {'adv_list':adv_list,
               'last_wel_list': last_wel_list,
               'first_adv':first_adv,
               'last_adv':last_adv,
               'adv_today1':adv_today1,
               'adv_today2':adv_today2,
               'adv_today3':adv_today3,
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
    return render(request, 'm_index.html', context)

def finance(request, id=None):
    if id is None:
        adv_list = list(Advertisement.objects.filter(location__in=['0','4'],is_hidden=False)[0:8])
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
        other_wel_list = Finance.objects.filter(state='1').order_by('-view_count')[0:10]
        context = {'news':news,'type':'Finance','other_wel_list':other_wel_list}
        ref_url = request.META.get('HTTP_REFERER',"")
        if 'next=' in ref_url:
            context.update({'back':True})
        return render(request, 'm_detail_taskandfinance.html',context)
        
def task(request, id=None):
    if id is None:
        adv_list = list(Advertisement.objects.filter(location__in=['0','3'],is_hidden=False)[0:8])
        first_adv = adv_list[0] if adv_list else None
        last_adv = adv_list[-1] if adv_list else None
#         hot_wel_list = Welfare.objects.filter(is_display=True,state='1').order_by('-view_count')[0:3]
        context = {'adv_list':adv_list, 'first_adv':first_adv, 'last_adv':last_adv,}
        return render(request, 'm_task.html', context)
    else:
        id = int(id)
        news = None
        try:
            news = Task.objects.get(id=id)
        except Task.DoesNotExist:
            raise Http404(u"该页面不存在")
        update_view_count(news)
        other_wel_list = Task.objects.filter(state='1').order_by('-view_count')[0:10]
        context = {'news':news,'type':'Task','other_wel_list':other_wel_list}
        ref_url = request.META.get('HTTP_REFERER',"")
        if 'next=' in ref_url:
            context.update({'back':True})
        return render(request, 'm_detail_taskandfinance.html', context)
    
def commodity(request, id):
    id = int(id)
    try:
        com = Commodity.objects.get(id=id)
    except Commodity.DoesNotExist:
        raise Http404(u"该页面不存在")
    return render(request, 'detail-commodity.html',{'com':com})
def press(request, id):
    id = int(id)
    try:
        press = Press.objects.get(id=id)
    except Press.DoesNotExist:
        raise Http404(u"该页面不存在")
    return render(request, 'detail-press.html',{'press':press})

def aboutus(request):
    ad_list = Advertisement.objects.filter(location__in=['0','6'],is_hidden=False).first
    return render(request, 'aboutus.html',{'ad_list':ad_list})

# def experience_taskandfinance(request):
#     if not request.is_ajax():
#         logger.warning("Experience refused no-ajax request!!!")
#         raise Http404
#     code = '0'
#     url = ''
#     if not request.user.is_authenticated():
#         url = reverse('login') + '?next=' + request.META['HTTP_REFERER']
#         result = {'code':code, 'url':url}
#         return JsonResponse(result)
#     news_id = request.GET.get('id', None)
#     news_type = request.GET.get('type', None)
#     if not (news_id and news_type):
#         logger.error("news_id or news_type is missing!!!")
#         raise Http404
#     news = None
#     model = globals()[news_type]
#     news = model.objects.get(pk=news_id)
#     code = '1'
#     if news.isonMobile:
#         url = news.exp_code.url
#     else:
#         url = news.exp_url
#     result = {'code':code, 'url':url}
#     return JsonResponse(result)
def expsubmit(request):
    if not request.is_ajax():
        logger.warning("Expsubmit refused no-ajax request!!!")
        raise Http404
    code = '0'
    url = ''
    if not request.user.is_authenticated():
        url = reverse('login') + '?next=' + request.META['HTTP_REFERER']
        result = {'code':code, 'url':url}
        return JsonResponse(result)
    news_id = request.POST.get('id', None)
    news_type = request.POST.get('type', None)
    is_futou = request.POST.get('is_futou', '0')
    telnum = request.POST.get('telnum', None)
    telnum = str(telnum).strip()
    remark = request.POST.get('remark', '')
    if not (news_id and news_type and telnum):
        logger.error("news_id or news_type is missing!!!")
        raise Http404
    if len(telnum)>100 or len(remark)>200:
        code = '3'
        msg = u'账号或备注过长！'
        result = {'code':code, 'msg':msg}
        return JsonResponse(result)
    news = None
    model = globals()[news_type]
#     if news.state != '1':
#         code = '4'
#         msg = u'该项目已结束或未开始！'
#         result = {'code':code, 'msg':msg}
#         return JsonResponse(result)
    if str(is_futou)=='1':
        remark = u"复投：" + remark
    try:
        with transaction.atomic():
            news = model.objects.get(pk=news_id)
            info_str = "news_id:" + news_id + "| invest_account:" + telnum + "| is_futou:" + is_futou
            logger.info(info_str)
            if str(is_futou)!='1' and news.user_event.filter(invest_account=telnum).exclude(audit_state='2').exists():
                raise ValueError('This invest_account is repective in project:' + str(news.id))
            else:
                UserEvent.objects.create(user=request.user, event_type='1', invest_account=telnum,
                                 content_object=news, audit_state='1',remark=remark,)
                code = '1'
                msg = u'提交成功，请通过用户中心查询！'
    except Exception, e:
        logger.info(e)
        code = '2'
        msg = u'该注册手机号已被提交过，请不要重复提交！'
    result = {'code':code, 'msg':msg}
    return JsonResponse(result)

def mall(request):
    ad_list = Advertisement.objects.filter(location__in=['0','5'],is_hidden=False)[0:8]
    help_list = Press.objects.filter(type='5')[0:10]
    type = request.GET.get("type", "")
    return render(request, 'mall.html', {'ad_list':ad_list,'type':type,'help_list':help_list})
def get_commodity_page(request):
    res={'code':0,}
    page = request.GET.get("page", None)
    size = request.GET.get("size", 16)
    cat = request.GET.get("cat", None)
    pro = request.GET.get("pro", None)
    try:
        size = int(size)
    except ValueError:
        size = 16
    if not page or size <= 0:
        raise Http404
    item_list = Commodity.objects.all()
    if cat:
        item_list = item_list.filter(category=cat)
    if pro:
        item_list = item_list.filter(item=pro)
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
        i = {"name":con.name,
             "price":con.price,
             "url":con.url,
             "pic":con.pic.url,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

#查询订单详情
def lookup_order(request):
    if not request.is_ajax():
        raise Http404
    result={'code':-1, 'url':''}
    if not request.user.is_authenticated():
        result['code'] = -1
        result['url'] = reverse('login') + "?next=" + reverse('account_score')
        return JsonResponse(result)   
    id = request.GET.get("id", None)
    if not id:
        return Http404
    try:
        id = int(id)
    except ValueError:
        return Http404
    try:
        record = ExchangeRecord.objects.get(tranlist_id=id)
    except ExchangeRecord.DoesNotExist: 
        result['code'] = 1
    except Exception as e:
        logger.error(e.reason)
    else:
        result['name'] = record.name
        result['tel'] = record.tel
        result['addr'] = record.addr
        result['mes'] = record.message
        result['code'] = 0
    return JsonResponse(result)

def submit_order(request):
    if not request.is_ajax():
        raise Http404
    result={'code':-1, 'url':''}
    if not request.user.is_authenticated():
        result['code'] = -1
        result['url'] = reverse('login') + "?next=" + reverse('account_score')
        return JsonResponse(result)   
    name = request.GET.get("name", '')
    tel = request.GET.get("tel", '')
    addr = request.GET.get("addr", '')
    remark= request.GET.get("remark", '')
    good_id= request.GET.get("id", '')
    if not (name and tel and addr and good_id):
        return Http404
    try:
        good_id = int(good_id)
    except ValueError:
        return Http404
    commodity = Commodity.objects.get(pk=good_id)
    ret = charge_score(request.user, '1', commodity.price, commodity.name)
    if ret is not None:
        logger.debug('Exchanging scores is successfully reduced!')
        exg_obj = ExchangeRecord.objects.create(tranlist=ret,commodity=commodity,
                                      name=name,tel=tel,addr=addr,message=remark)
        event = UserEvent.objects.create(user=request.user, event_type='3',invest_amount=commodity.price,
                         audit_state='1',remark=remark, content_object=exg_obj)
        ret.user_event = event
        ret.save(update_fields=['user_event'])
        result['code'] = 0
    else:
        logger.debug('Exchanging scores is failed to reduce!!!')
        result['code'] = 1
    return JsonResponse(result)

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
def get_task_page(request):
    res={'code':0,}
    page = request.GET.get("page", None)
    size = request.GET.get("size", 6)
    filter = request.GET.get("filter", 0)
    state = request.GET.get("state", 0)
    try:
        size = int(size)
    except ValueError:
        size = 6
    if not page or size <= 0:
        raise Http404
    item_list = Task.objects.all()
    filter = str(filter)
    state = str(state)
    if filter == '1':
        item_list = item_list.filter(amount_to_invest=0)
    elif filter == '2':
        item_list = item_list.filter(amount_to_invest__lte=100)
    elif filter == '3':
        item_list = item_list.filter(amount_to_invest__gt=100)
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
             "url":con.url,
             "time":con.time_limit,
             "pic":con.pic.url,
             "view":con.view_count,
             'provider':con.provider,
             "is_new":'new' if con.is_new() else '',
        }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)
def get_wel_page(request):
    res={'code':0,}
    page = request.GET.get("page", None)
    size = request.GET.get("size", 6)
    filter = request.GET.get("filter", 0)
    state = request.GET.get("state", 0)
    try:
        size = int(size)
    except ValueError:
        size = 6
    if not page or size <= 0:
        raise Http404
    item_list = Welfare.objects.all()
    filter = str(filter)
    state = str(state)
    if filter != '0':
        item_list = item_list.filter(zero_type=filter)
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
             "url":con.url,
             "time":con.time_limit,
             "pic":con.pic.url,
             "view":con.view_count,
             'provider':con.provider,
             "is_new":'new' if con.is_new() else '',
        }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)
def get_press_page(request):
    res={'code':0,}
    page = request.GET.get("page", None)
    size = request.GET.get("size", 5)
    type = request.GET.get("type", 0)
    try:
        size = int(size)
    except ValueError:
        size = 6
    if not page or size <= 0:
        raise Http404
    item_list = Press.objects.all()
    type = str(type)
    if type != '0':
        item_list = item_list.filter(type=type)
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
             "url":con.url,
             "time":con.pub_date.strftime("%Y-%m-%d"),
             "view":con.view_count,
             "summary":con.summary,
        }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

def freshman_introduction(request):
    return render(request, "freshman_introduction.html")
def freshman_award(request):
    return render(request, "freshman_award.html")

def business(request, page=None):
    if not page:
        page = 1
    else:
        page = int(page)
    hot_business_list = Company.objects.order_by('-view_count')[0:8]
    business_list = Company.objects.all()
    search_key = request.GET.get('key', '')
    if search_key:
        business_list = business_list.filter(name__contains=search_key)
    business_list, page_num = listing(business_list, 36, page)
    full_path = str(request.get_full_path())
    path_split = []
    if 'list-page' in full_path:
        path_split = re.split('list-page\d+',full_path)
    elif '?' in full_path:
        path_split = full_path.split('?')
        path_split[1] = '?' + path_split[1]
    else:
        path_split=[full_path, '']
    page_dic = {}
    page_dic['pre_path'] = path_split[0]
    page_dic['suf_path'] = path_split[1]
    page_list = []
    if page_num < 10:
        page_list = range(1,page_num+1)
    else:
        if page < 6:
            page_list = range(1,8) + ["...",page_num]
        elif page > page_num - 5:
            page_list = [1,'...'] + range(page_num-6, page_num+1)
        else:
            page_list = [1,'...'] + range(page-2, page+3) + ['...',page_num]
    page_dic['page_list'] = page_list
    hot_wel_list = Welfare.objects.filter(is_display=True, state='1').order_by('-view_count')[0:8]
    content = {
        'page_dic':page_dic,
        'hot_business_list':hot_business_list,
        'business_list':business_list,
        'hot_wel_list':hot_wel_list,
    }
    return render(request, "business.html", content)

def information(request, id=None):
    if not id:
        return render(request, 'm_information.html')
    elif id:
        id = int(id)
        info = None
        try:
            info = Information.objects.get(id=id)
        except Information.DoesNotExist:
            raise Http404(u"该页面不存在")
        update_view_count(info)
        hot_info_list = Information.objects.filter(is_display=True).order_by('-view_count')[0:3]
        return render(request, 'm_detail_information.html',{'info':info, 'hot_info_list':hot_info_list, 'type':'Information'})