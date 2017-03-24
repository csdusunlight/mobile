#coding:utf-8
from django.shortcuts import render, redirect
from wafuli.models import UserEvent, AdminEvent, AuditLog, TransList, Company,\
    Finance, Task, Welfare, Message
import datetime
from django.db.models import Sum, Count
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse, Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from account.transaction import charge_money, charge_score
import logging
from account.models import MyUser
from django.db.models import Q,F
from wafuli_admin.models import DayStatis, Invest_Record
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import logout as auth_logout
from account.varify import send_multimsg_bydhst
# Create your views here.
logger = logging.getLogger('wafuli')
def index(request):
    admin_user = request.user
    if not ( admin_user.is_authenticated() and admin_user.is_staff):
        return redirect(reverse('admin:login') + "?next=" + reverse('admin_index'))
    today = datetime.date.today()
#     day = datetime.datetime.strptime('2015-01-01','%Y-%m-%d')
#     with_num_today = UserEvent.objects.filter(event_type='2',time__gte=today,audit_state='1').count()
#     with_num = UserEvent.objects.filter(event_type='2',audit_state='1').count()
#     ret_num_today = UserEvent.objects.filter(event_type='1',time__gte=today,audit_state='1').count()
#     ret_num = UserEvent.objects.filter(event_type='1',audit_state='1').count()
    query = UserEvent.objects.filter(audit_state='1').values('event_type')\
                .annotate(sum=Count('*')).order_by()
    query_today = UserEvent.objects.filter(audit_state='1',time__gte=today).values('event_type')\
                .annotate(sum=Count('*')).order_by()
#     print query,query_today
#     num_today = {'with_num_today':0,'ret_num_today':0,'coupon_num_today':0,'exc_num_today':0,}
#     num = {'with_num':0,'ret_num':0,'coupon_num':0,'exc_num':0}
    num_today = {'1':0,'2':0,'3':0,'4':0,'6':0}
    num = {'1':0,'2':0,'3':0,'4':0,'6':0}
    for q in query:
        index = q.get('event_type')
        num[index] = q.get('sum')
    for q in query_today:
        index = q.get('event_type')
        num_today[index] = q.get('sum')
#     print num,num_today
    total = {}
    dict1 = MyUser.objects.aggregate(cou=Count('id'), sumb=Sum('balance'),sums=Sum('scores'))
    total['user_num'] = dict1.get('cou')
    total['balance'] = (dict1.get('sumb') or 0)/100.0
    total['score'] = dict1.get('sums')
#     print TransList.objects.filter(user_event__event_type='2',user_event__audit_state='0').aggregate(cou=Count('id'),sum=Sum('transAmount'))
    dict_with = UserEvent.objects.filter(event_type='2',audit_state='0').\
            aggregate(cou=Count('user',distinct=True),sum=Sum('translist__transAmount'))
    total['with_count'] = dict_with.get('cou')
    total['with_total'] = (dict_with.get('sum') or 0)/100.0
    
    dict_ret = UserEvent.objects.filter(event_type='1',audit_state='0').\
            aggregate(cou=Count('user',distinct=True),sum=Sum('translist__transAmount'))
    total['ret_count'] = dict_ret.get('cou')
    total['ret_total'] = (dict_ret.get('sum') or 0)/100.0
    
    dict_coupon = UserEvent.objects.filter(event_type='4',audit_state='0').\
            aggregate(sum=Sum('translist__transAmount'))
    total['coupon_total'] = (dict_coupon.get('sum') or 0)/100.0
    
    dict_score = UserEvent.objects.filter(event_type='3',audit_state='0').\
            aggregate(sum=Sum('score_translist__transAmount'))
    total['ret_count'] = (dict_ret.get('cou') or 0)
    total['score_exchange_total'] = dict_score.get('sum')
    return render(request,"admin_index.html",{'num':num,'num_today':num_today,'total':total})

def get_admin_index_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_index')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    try:
        size = int(size)
    except ValueError:
        size = 10
    if not page or size <= 0:
        raise Http404
    item_list = []
    item_list = DayStatis.objects.all()
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%d')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%d')
        item_list = item_list.filter(date__range=(s,e))
    
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
        i = {"date":con.date,
             "new_reg_num":con.new_reg_num,
             "active_num":con.active_num,
             "with_amount":con.with_amount/100.0,
             "with_num":con.with_num,
             "ret_amount":con.ret_amount/100.0,
             "ret_scores":con.ret_scores,
             "ret_num":con.ret_num,
             "coupon_amount":con.coupon_amount,
             "exchange_scores":con.exchange_scores,
             "lottery_people":con.lottery_people,
             "lottery_num":con.lottery_num,
             "envelope_people":con.envelope_people,
             "envelope_num":con.envelope_num,
             "envelope_money":con.envelope_money,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

def admin_finance(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_finance'))
        return render(request,"admin_finance.html")
    if request.method == "POST":
        res = {}
        if not request.is_ajax():
            raise Http404
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            res['code'] = -1
            res['url'] = reverse('admin:login') + "?next=" + reverse('admin_finance')
            return JsonResponse(res)
        if not admin_user.has_admin_perms('002'):
            res['code'] = -5
            res['res_msg'] = u'您没有操作权限！'
            return JsonResponse(res) 
        event_id = request.POST.get('id', None)
        cash = request.POST.get('cash', None)
        score = request.POST.get('score', None)
        type = request.POST.get('type', None)
        reason = request.POST.get('reason', None)
        type = int(type)
        if not event_id or type==1 and not (cash and score) or type==2 and not reason or type!=1 and type!=2:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        event = UserEvent.objects.get(id=event_id)
        event_user = event.user
        log = AuditLog(user=admin_user,item=event)
        translist = None
        scoretranslist = None
        if type==1:
            try:
                cash = float(cash)*100
                cash = int(cash)
                score = int(score)
            except:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if cash < 0 or score < 0:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if event.audit_state != '1':
                res['code'] = -3
                res['res_msg'] = u'该项目已审核过，不要重复审核！'
                return JsonResponse(res)
            if event.translist.exists():
                logger.critical("Returning cash is repetitive!!!")
                res['code'] = -3
                res['res_msg'] = u"操作失败，返现重复！"
            else:
                log.audit_result = True
                translist = charge_money(event_user, '0', cash, u'福利返现')
                scoretranslist = charge_score(event_user, '0', score, u'福利返现（积分）')
                if translist and scoretranslist:
                    event.audit_state = '0'
                    translist.user_event = event
                    translist.save(update_fields=['user_event'])
                    scoretranslist.user_event = event
                    scoretranslist.save(update_fields=['user_event'])
                    res['code'] = 0
                    #更新投资记录表
                    Invest_Record.objects.create(invest_date=event.time,invest_company=event.content_object.company.name,
                                                 user_name=event_user.zhifubao_name,zhifubao=event_user.zhifubao,
                                                 invest_mobile=event.invest_account,invest_period=event.invest_term,
                                                 invest_amount=event.invest_amount,return_amount=cash/100.0,wafuli_account=event_user.mobile,
                                                 return_date=datetime.date.today(),remark=event.remark)    
                    msg_content = u'您提交的"' + event.content_object.title + u'"理财福利已审核通过。'
                    Message.objects.create(user=event_user, content=msg_content, title=u"福利审核");
                else:
                    res['code'] = -4
                    res['res_msg'] = "注意，重复提交时只提交失败项目，成功的可以输入0。\n"
                    if not translist:
                        logger.error(u"Charging cash is failed!!!")
                        res['res_msg'] += u"现金记账失败，请检查输入合法性后再次提交！"
                    if not scoretranslist:
                        logger.error(u"Charging score is failed!!!")
                        res['res_msg'] += u"积分记账失败，请检查输入合法性后再次提交！"
        else:
            event.audit_state = '2'
            log.audit_result = False
            log.reason = reason
            res['code'] = 0
            
            msg_content = u'您提交的"' + event.content_object.title + u'"理财福利审核未通过，原因：' + reason
            Message.objects.create(user=event_user, content=msg_content, title=u"福利审核");
        
        
        if res['code'] == 0:
            admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event_user, event_type='1')
            if translist:
                translist.admin_event = admin_event
                translist.save(update_fields=['admin_event'])
            if scoretranslist:
                scoretranslist.admin_event = admin_event
                scoretranslist.save(update_fields=['admin_event'])
            log.admin_item = admin_event
            log.save()
            event.audit_time = log.time
            event.save(update_fields=['audit_state','audit_time'])
        return JsonResponse(res)

def admin_task(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_task'))
        return render(request,"admin_task.html")
    if request.method == "POST":
        res = {}
        if not request.is_ajax():
            raise Http404
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            res['code'] = -1
            res['url'] = reverse('admin:login') + "?next=" + reverse('admin_task')
            return JsonResponse(res)
        if not admin_user.has_admin_perms('002'):
            res['code'] = -5
            res['res_msg'] = u'您没有操作权限！'
            return JsonResponse(res) 
        event_id = request.POST.get('id', None)
        cash = request.POST.get('cash', None)
        score = request.POST.get('score', None)
        type = request.POST.get('type', None)
        reason = request.POST.get('reason', None)
        type = int(type)
        if not event_id or type==1 and not (cash and score) or type==2 and not reason or type!=1 and type!=2:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        event = UserEvent.objects.get(id=event_id)
        event_user = event.user
        log = AuditLog(user=admin_user,item=event)
        translist = None
        scoretranslist = None
        if type==1:
            try:
                cash = float(cash)*100
                cash = int(cash)
                score = int(score)
            except:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if cash < 0 or score < 0:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if event.audit_state != '1':
                res['code'] = -3
                res['res_msg'] = u'该项目已审核过，不要重复审核！'
                return JsonResponse(res)
            if event.translist.exists():
                logger.critical("Returning cash is repetitive!!!")
                res['code'] = -3
                res['res_msg'] = u"操作失败，返现重复！"
            else:
                log.audit_result = True
                translist = charge_money(event_user, '0', cash, u'福利返现')
                scoretranslist = charge_score(event_user, '0', score, u'福利返现（积分）')
                if translist and scoretranslist:
                    event.audit_state = '0'
                    translist.user_event = event
                    translist.save(update_fields=['user_event'])
                    scoretranslist.user_event = event
                    scoretranslist.save(update_fields=['user_event'])
                    res['code'] = 0
                    msg_content = u'您提交的"' + event.content_object.title + u'"体验福利已审核通过。'
                    Message.objects.create(user=event_user, content=msg_content, title=u"福利审核");
                else:
                    res['code'] = -4
                    res['res_msg'] = "注意，重复提交时只提交失败项目，成功的可以输入0。\n"
                    if not translist:
                        logger.error(u"Charging cash is failed!!!")
                        res['res_msg'] += u"现金记账失败，请检查输入合法性后再次提交！"
                    if not scoretranslist:
                        logger.error(u"Charging score is failed!!!")
                        res['res_msg'] += u"积分记账失败，请检查输入合法性后再次提交！"
        else:
            event.audit_state = '2'
            log.audit_result = False
            log.reason = reason
            task = event.content_object
            task.left_num = F("left_num")+1
            task.save(update_fields=['left_num'])
            res['code'] = 0
        
            msg_content = u'您提交的"' + event.content_object.title + u'"体验福利审核未通过，原因：' + reason
            Message.objects.create(user=event_user, content=msg_content, title=u"福利审核");
        
        if res['code'] == 0:
            admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event_user, event_type='1')
            if translist:
                translist.admin_event = admin_event
                translist.save(update_fields=['admin_event'])
            if scoretranslist:
                scoretranslist.admin_event = admin_event
                scoretranslist.save(update_fields=['admin_event'])
            log.admin_item = admin_event
            log.save()
            event.audit_time = log.time
            event.save(update_fields=['audit_state','audit_time'])
        return JsonResponse(res)
    
def get_admin_finance_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_finance')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    state = request.GET.get("state",'1')
    try:
        size = int(size)
    except ValueError:
        size = 10

    if not page or size <= 0 or not state:
        raise Http404
    item_list = []

    item_list = UserEvent.objects
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    startTime2 = request.GET.get("startTime2", None)
    endTime2 = request.GET.get("endTime2", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(time__range=(s,e))
    if startTime2 and endTime2:
        s = datetime.datetime.strptime(startTime2,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime2,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(audit_time__range=(s,e))
        
    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(user__username=username)
    
    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)
        
    companyname = request.GET.get("companyname", None)
    if companyname:
        item_list = item_list.filter(finance__company__name__contains=companyname)
        
    projectname = request.GET.get("projectname", None)
    if projectname:
        item_list = item_list.filter(finance__title__contains=projectname)
        
    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)
    task_type = ContentType.objects.get_for_model(Finance)
    item_list = item_list.filter(content_type = task_type.id)
    item_list = item_list.filter(event_type='1', audit_state=state).select_related('user').order_by('time')
    
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
        project = con.content_object
        i = {"username":con.user.username,
             "mobile":con.user.mobile,
             "type":con.content_object.get_type(),
             "company":project.company.name if project.company else u"无",
             "project":project.title,
             "mobile_sub":con.invest_account,
             "remark_sub":con.remark,
             "time_sub":con.time.strftime("%Y-%m-%d %H:%M"),
             "state":con.get_audit_state_display(),
             "admin":u'无' if con.audit_state=='1' or not con.audited_logs.exists() else con.audited_logs.first().user.username,
             "time_admin":u'无' if con.audit_state=='1' or not con.audit_time else con.audit_time.strftime("%Y-%m-%d %H:%M"),
             "ret_amount":u'无' if con.audit_state!='0' or not con.translist.exists() else con.translist.first().transAmount/100.0,
             "score":u'无' if con.audit_state!='0' or not con.score_translist.exists() else con.score_translist.first().transAmount,
             "id":con.id,
             "remark": con.remark or u'无' if con.audit_state!='2' or not con.audited_logs.exists() else con.audited_logs.first().reason,
             "invest_amount": con.invest_amount,
             "term": con.invest_term,
        }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

def get_admin_task_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_task')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    state = request.GET.get("state",'1')
    try:
        size = int(size)
    except ValueError:
        size = 10

    if not page or size <= 0 or not state:
        raise Http404
    item_list = []

    item_list = UserEvent.objects
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    startTime2 = request.GET.get("startTime2", None)
    endTime2 = request.GET.get("endTime2", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(time__range=(s,e))
    if startTime2 and endTime2:
        s = datetime.datetime.strptime(startTime2,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime2,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(audit_time__range=(s,e))
        
    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(user__username=username)
    
    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)
        
    companyname = request.GET.get("companyname", None)
    if companyname:
        item_list = item_list.filter(task__company__name__contains=companyname)
        
    projectname = request.GET.get("projectname", None)
    if projectname:
        item_list = item_list.filter(task__title__contains=projectname)
        
    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)
    task_type = ContentType.objects.get_for_model(Task)
    item_list = item_list.filter(content_type = task_type.id)
    item_list = item_list.filter(event_type='1', audit_state=state).select_related('user').order_by('time')
    
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
        project = con.content_object
        i = {"username":con.user.username,
             "mobile":con.user.mobile,
             "type":con.content_object.get_type(),
             "company":project.company.name if project.company else u"无",
             "project":project.title,
             "mobile_sub":con.invest_account,
             "remark_sub":con.remark,
             "time_sub":con.time.strftime("%Y-%m-%d %H:%M"),
             "state":con.get_audit_state_display(),
             "admin":u'无' if con.audit_state=='1' or not con.audited_logs.exists() else con.audited_logs.first().user.username,
             "time_admin":u'无' if con.audit_state=='1' or not con.audit_time else con.audit_time.strftime("%Y-%m-%d %H:%M"),
             "ret_amount":u'无' if con.audit_state!='0' or not con.translist.exists() else con.translist.first().transAmount/100.0,
             "score":u'无' if con.audit_state!='0' or not con.score_translist.exists() else con.score_translist.first().transAmount,
             "id":con.id,
             "remark": con.remark or u'无' if con.audit_state!='2' or not con.audited_logs.exists() else con.audited_logs.first().reason,
        }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

def admin_user(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_user'))
        return render(request,"admin_user.html")
    if request.method == "POST":
        res = {}
        if not admin_user.has_admin_perms('005'):
            res['code'] = -5
            res['res_msg'] = u'您没有操作权限！'
            return JsonResponse(res)
        if not request.is_ajax():
            raise Http404
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            res['code'] = -1
            res['url'] = reverse('admin:login') + "?next=" + reverse('admin_user')
            return JsonResponse(res)
        user_id = request.POST.get('id', None)
        type = request.POST.get('type', None)
        type = int(type)
#         if not user_id or type==1 and not (cash and score) or type==2 and not reason or type!=1 and type!=2:
#             res['code'] = -2
#             res['res_msg'] = u'传入参数不足，请联系技术人员！'
#             return JsonResponse(res)
        obj_user = MyUser.objects.get(id=user_id) 
        if type==1:
            pcash = request.POST.get('pcash', 0)
            mcash = request.POST.get('mcash', 0)
            if not pcash:
                pcash = 0
            if not mcash:
                mcash = 0
            reason = request.POST.get('reason', '')
            if not pcash and not mcash or pcash and mcash or not reason:
                res['code'] = -2
                res['res_msg'] = u'传入参数不足，请联系技术人员！'
                return JsonResponse(res)
            try:
                pcash = float(pcash)*100
                pcash = int(pcash)
                mcash = float(mcash)*100
                mcash = int(mcash)
            except:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if pcash < 0 or mcash < 0:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            translist = None
            if pcash > 0:
                translist = charge_money(obj_user, '0', pcash, reason)
            elif mcash > 0:
                translist = charge_money(obj_user, '1', mcash, reason)
            if translist:
                admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=obj_user, remark=reason, event_type='4')
                translist.admin_event = admin_event
                translist.save(update_fields=['admin_event'])
                res['code'] = 0
            else:
                res['code'] = -4
                res['res_msg'] = "现金记账失败，请检查输入合法性后再次提交！"
        elif type == 2:
            pscore = request.POST.get('pscore', 0)
            mscore = request.POST.get('mscore', 0)
            if not pscore:
                pscore = 0
            if not mscore:
                mscore = 0
            reason = request.POST.get('reason', '')
            if not pscore and not mscore or pscore and mscore or not reason:
                res['code'] = -2
                res['res_msg'] = u'传入参数不足，请联系技术人员！'
                return JsonResponse(res)
            try:
                pscore = int(pscore)
                mscore = int(mscore)
            except:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            if pscore < 0 or mscore < 0:
                res['code'] = -2
                res['res_msg'] = u"操作失败，输入不合法！"
                return JsonResponse(res)
            
            scoretranslist = None
            if pscore > 0:
                scoretranslist = charge_score(obj_user, '0', pscore, reason)
            elif mscore > 0:
                scoretranslist = charge_score(obj_user, '1', mscore, reason)
            if scoretranslist:
                admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=obj_user, remark=reason,event_type='5')
                scoretranslist.admin_event = admin_event
                scoretranslist.save(update_fields=['admin_event'])
                res['code'] = 0
            else:
                res['code'] = -4
                res['res_msg'] = "积分记账失败，请检查输入合法性后再次提交！"
        elif type == 3:
            obj_user.is_active = False
            obj_user.save(update_fields=['is_active'])
            auth_logout(request)
            admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=obj_user, event_type='6', remark=u"加黑")
            res['code'] = 0
        elif type == 4:
            obj_user.is_active = True
            obj_user.save(update_fields=['is_active'])
            admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=obj_user, event_type='6', remark=u"去黑")
            res['code'] = 0
        return JsonResponse(res)
            
def get_admin_user_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_user')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    state = request.GET.get("state",'0')
    
    try:
        size = int(size)
    except ValueError:
        size = 10

    if not page or size <= 0:
        raise Http404
    item_list = []

    item_list = MyUser.objects.all()
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    startTime2 = request.GET.get("startTime2", None)
    endTime2 = request.GET.get("endTime2", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(date_joined__range=(s,e))
    if startTime2 and endTime2:
        s = datetime.datetime.strptime(startTime2,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime2,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(this_login_time__range=(s,e))
        
    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(username=username)
    
    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(mobile=mobile)
        
    inviter_name = request.GET.get("inviter_name", None)
    if inviter_name:
        item_list = item_list.filter(inviter__username=inviter_name)
        
    inviter_mobile = request.GET.get("inviter_mobile", None)
    if inviter_mobile:
        item_list = item_list.filter(inviter__mobile=inviter_mobile)
        
    if state=='1':
        item_list = item_list.filter(is_active=False)
    elif state=='2':
        item_list = item_list.filter(is_active=True)
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
        inviter_username = u'无'
        inviter_mobile = u'无'
        inviter = con.inviter
        if inviter:
            inviter_username = inviter.username
            inviter_mobile = inviter.mobile
        recent_login_time = u'无'
        if con.this_login_time:
            recent_login_time = con.this_login_time.strftime("%Y-%m-%d %H:%M")
        i = {"username":con.username,
             "mobile":con.mobile,
             "email":con.email,
             "zhifubao":con.zhifubao,
             "zhifubao_name":con.zhifubao_name,
             "time":con.date_joined.strftime("%Y-%m-%d %H:%M"),
             'recent_login_time':recent_login_time,
             "inviter_name":inviter_username,
             "inviter_mobile":inviter_mobile,
             "balance":con.balance/100.0,
             "is_black":u'否' if con.is_active else u'是',
             "id":con.id,
             "opertype":u'加黑' if con.is_active else u'去黑',
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

def admin_withdraw(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_withdraw'))
        return render(request,"admin_withdraw.html")
    if request.method == "POST":
        res = {}
        if not admin_user.has_admin_perms('004'):
            res['code'] = -5
            res['res_msg'] = u'您没有操作权限！'
            return JsonResponse(res)
        if not request.is_ajax():
            raise Http404
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            res['code'] = -1
            res['url'] = reverse('admin:login') + "?next=" + reverse('admin_user')
            return JsonResponse(res)
        event_id = request.POST.get('id', None)
        type = request.POST.get('type', None)
        if not event_id or not type:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        type = int(type)
        event_id = int(event_id)
        event = UserEvent.objects.get(id=event_id)
        if event.audit_state != '1':
            res['code'] = -3
            res['res_msg'] = u'该项目已审核过，不要重复审核！'
            return JsonResponse(res)
        log = AuditLog(user=admin_user,item=event)
        admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event.user, event_type='2')
        if type==1:
            event.audit_state = '0'
            log.audit_result = True
            res['code'] = 0
            #用户首次提现成功，立即发放邀请人100积分和三个随机红包奖励
            inviter = event.user.inviter
            if inviter:
                if not UserEvent.objects.filter(user=event.user, event_type='2', audit_state='0').exists():
                    invite_award_scores = settings.AWARD_SCORES
                    inviter.invite_scores += invite_award_scores
                    translist = charge_score(inviter, '0', invite_award_scores, u"邀请奖励")
                    if translist:
                        logger.debug('Inviting Award scores is successfully payed!')
                        inviter.save(update_fields=['invite_scores'])
                        translist.user_event = event
                        translist.admin_event = admin_event
                        translist.save(update_fields=['user_event','admin_event'])
                    else:
                        logger.debug('Inviting Award scores is failed to pay!!!')
            trans_withdraw = event.translist.first()
            if trans_withdraw:
                trans_withdraw.admin_event = admin_event
                trans_withdraw.save(update_fields=['admin_event'])
            msg_content = u'您提现的' + str(event.invest_amount) + u'福币，已发放到您的支付宝账号中，请注意查收'
            Message.objects.create(user=event.user, content=msg_content, title=u"提现审核")
        
        elif type == 2:
            reason = request.POST.get('reason', '')
            if not reason:
                res['code'] = -2
                res['res_msg'] = u'传入参数不足，请联系技术人员！'
                return JsonResponse(res)
            event.audit_state = '2'
            log.reason = reason
            log.audit_result = False
            translist = charge_money(event.user, '0', event.invest_amount, u'冲账')
            if translist:
                translist.user_event = event
                translist.admin_event = admin_event
                translist.save(update_fields=['user_event','admin_event'])
                res['code'] = 0
                msg_content = u'您提现的' + str(event.invest_amount) + u'福币未审核成功，原因：' + reason
                Message.objects.create(user=event.user, content=msg_content, title=u"提现审核");
            else:
                logger.critical(u"Charging cash is failed!!!")
                res['code'] = -2
                res['res_msg'] = u"现金记账失败，请检查输入合法性后再次提交！"
                return JsonResponse(res)
        log.admin_item = admin_event
        log.save()
        event.audit_time = log.time
        event.save(update_fields=['audit_state','audit_time'])
        return JsonResponse(res)
            
def get_admin_with_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_withdraw')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    state = request.GET.get("state",'1')
    
    try:
        size = int(size)
    except ValueError:
        size = 10

    if not page or size <= 0:
        raise Http404
    item_list = []

    item_list = UserEvent.objects
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    startTime2 = request.GET.get("startTime2", None)
    endTime2 = request.GET.get("endTime2", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(time__range=(s,e))
    if startTime2 and endTime2:
        s = datetime.datetime.strptime(startTime2,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime2,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(audit_time__range=(s,e))
        
    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(user__username=username)
    
    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)
        
    zhifubao = request.GET.get("zhifubao", None)
    if zhifubao:
        item_list = item_list.filter(user__zhifubao=zhifubao)
        
    zhifubao_name = request.GET.get("zhifubao_name", None)
    if zhifubao_name:
        item_list = item_list.filter(user__zhifubao_name=zhifubao_name)
        
    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)
    item_list = item_list.filter(event_type='2', audit_state=state).select_related('user').order_by('time')
    
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
        obj_user = con.user
        i = {"username":obj_user.username,
             "mobile":obj_user.mobile,
             "balance":obj_user.balance/100.0,
             "zhifubao_name":obj_user.zhifubao_name,
             "zhifubao":obj_user.zhifubao,
             "amount":con.invest_amount/100.0,
             "time":con.time.strftime("%Y-%m-%d %H:%M"),
             "state":con.get_audit_state_display(),
             "admin":u'无' if con.audit_state=='1' or not con.audited_logs.exists() else con.audited_logs.first().user.username,
             "time_admin":u'无' if con.audit_state=='1' or not con.audit_time else con.audit_time.strftime("%Y-%m-%d %H:%M"),
             "id":con.id,
             "remark": con.remark or u'无' if con.audit_state!='2' or not con.audited_logs.exists() else con.audited_logs.first().reason,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

def admin_score(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_score'))
        return render(request,"admin_score.html")
    if request.method == "POST":
        res = {}
        if not admin_user.has_admin_perms('003'):
            res['code'] = -5
            res['res_msg'] = u'您没有操作权限！'
            return JsonResponse(res)
        if not request.is_ajax():
            raise Http404
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            res['code'] = -1
            res['url'] = reverse('admin:login') + "?next=" + reverse('admin_user')
            return JsonResponse(res)
        event_id = request.POST.get('id', None)
        type = request.POST.get('type', None)
        if not event_id or not type:
            res['code'] = -2
            res['res_msg'] = u'传入参数不足，请联系技术人员！'
            return JsonResponse(res)
        type = int(type)
        event_id = int(event_id)
        event = UserEvent.objects.get(id=event_id)
        log = AuditLog(user=admin_user,item=event)
        if event.audit_state != '1':
            res['code'] = -3
            res['res_msg'] = u'该项目已审核过，不要重复审核！'
            return JsonResponse(res)
        if type==1:
            event.audit_state = '0'
            log.audit_result = True
            res['code'] = 0
            msg_content = u'您已成功兑换' + event.content_object.commodity.name + u'，消耗积分' + event.invest_amount
            Message.objects.create(user=event.user, content=msg_content, title=u"积分兑换");
        elif type == 2:
            reason = request.POST.get('reason', '')
            if not reason:
                res['code'] = -2
                res['res_msg'] = u'传入参数不足，请联系技术人员！'
                return JsonResponse(res)
            event.audit_state = '2'
            log.reason = reason
            log.audit_result = False
            scoretranslist = charge_score(event.user, '0', event.invest_amount, u'冲账')
            if scoretranslist:
                scoretranslist.user_event = event
                scoretranslist.save(update_fields=['user_event'])
                res['code'] = 0
                msg_content = u'您兑换的' + event.content_object.commodity.name + u'未成功，原因：' + reason
                Message.objects.create(user=event.user, content=msg_content, title=u"积分兑换");
            else:
                logger.critical(u"Charging score is failed!!!")
                res['code'] = -2
                res['res_msg'] = u"现金记账失败，请检查输入合法性后再次提交！"
                return JsonResponse(res)
        admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event.user, event_type='8')
        log.admin_item = admin_event
        log.save()
        event.audit_time = log.time
        event.save(update_fields=['audit_state','audit_time'])
        return JsonResponse(res)
def get_admin_score_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_withdraw')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    state = request.GET.get("state",'1')
    
    try:
        size = int(size)
    except ValueError:
        size = 10

    if not page or size <= 0:
        raise Http404
    item_list = []
    item_list = UserEvent.objects
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    startTime2 = request.GET.get("startTime2", None)
    endTime2 = request.GET.get("endTime2", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(time__range=(s,e))
    if startTime2 and endTime2:
        s = datetime.datetime.strptime(startTime2,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime2,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(audit_time__range=(s,e))
        
    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(user__username=username)
    
    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)
        
    commodityname = request.GET.get("commodityname", None)
    if commodityname:
        item_list = item_list.filter(exchangerecord__commodity__name__contains=commodityname)
        
    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)
    item_list = item_list.filter(event_type='3', audit_state=state).select_related('user').order_by('time')
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
        obj_user = con.user
        exchange_record = con.content_object
        commodity = exchange_record.commodity
        i = {"username":obj_user.username,
             "mobile":obj_user.mobile,
             "title":commodity.name,
             "price":commodity.price,
             "score":obj_user.scores,
             "id":con.id,
             "order_id":exchange_record.tranlist.id,
             "amount":con.invest_amount,
             "time_sub":con.time.strftime("%Y-%m-%d %H:%M"),
             "state":con.get_audit_state_display(),
             "admin":u'无' if con.audit_state=='1' or not con.audited_logs.exists() else con.audited_logs.first().user.username,
             "time_admin":u'无' if con.audit_state=='1' or not con.audit_time else con.audit_time.strftime("%Y-%m-%d %H:%M"),
             "remark":u'无' if con.audit_state!='2' or not con.audited_logs.exists() else con.audited_logs.first().reason,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

def admin_charge(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_charge'))
        return render(request,"admin_charge.html")
    
def get_admin_charge_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_charge')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    try:
        size = int(size)
    except ValueError:
        size = 10

    if not page or size <= 0:
        raise Http404
    item_list = []

    item_list = TransList.objects.all()
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%dT%H:%M')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%dT%H:%M')
        item_list = item_list.filter(time__range=(s,e))
        
    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(user__username=username)
    
    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(user__mobile=mobile)
        
    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(admin_event__admin_user__username=adminname)
    
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
        i = {"username":con.user.username,
             "mobile":con.user.mobile,
             "time":con.time.strftime("%Y-%m-%d %H:%M"),
             "init_amount":con.initAmount/100.0,
             "charge_amount":('+' if con.transType=='0' else '-') + str(con.transAmount/100.0),
             "reason": con.reason,
             "remark": con.remark,
             "admin_user":u'无' if not con.admin_event else con.admin_event.admin_user.username,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

def admin_investrecord(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_investrecord'))
        return render(request,"admin_investrecord.html")
def get_admin_investrecord_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_investrecord')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    try:
        size = int(size)
    except ValueError:
        size = 10

    if not page or size <= 0:
        raise Http404
    item_list = []

    item_list = Invest_Record.objects.all()
    startTime = request.GET.get("startTime", None)
    endTime = request.GET.get("endTime", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%d')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%d')
        item_list = item_list.filter(invest_date__range=(s,e))
    amountfrom = request.GET.get("amountfrom", None)
    amountto = request.GET.get("amountto", None)
    if amountfrom and amountto:
        af = request.GET.get("amountfrom", 0)
        at = request.GET.get("amountto", 0)
        item_list = item_list.filter(invest_amount__range=(af,at))
    username = request.GET.get("username", None)
    if username:
        item_list = item_list.filter(user_name=username)
    
    mobile = request.GET.get("mobile", None)
    if mobile:
        item_list = item_list.filter(invest_mobile=mobile)
        
    projectname = request.GET.get("projectname", None)
    if projectname:
        item_list = item_list.filter(invest_company__contains=projectname)
    
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
        i = {
             "invest_date": con.invest_date.strftime("%Y-%m-%d") if con.invest_date else '',
             'invest_company':con.invest_company,
             'qq_number':con.qq_number,
             "user_name":con.user_name,
             "zhifubao":con.zhifubao,
             "invest_mobile":con.invest_mobile,
             'invest_period':con.invest_period,
             'invest_amount':con.invest_amount,
             'return_amount':con.return_amount,
             'wafuli_account':con.wafuli_account,
             }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

def send_multiple_msg(request):
    res={'code':0,}
    user = request.user
    content = request.POST.get('content')
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_investrecord')
        return JsonResponse(res)
    if not user.has_admin_perms('007'):
        res['code'] = -5
        res['res_msg'] = u'您没有操作权限！'
        return JsonResponse(res)
    if not content or len(content)==0:
        res['code'] = -6
        res['res_msg'] = u'短信内容不能为空！'
        return JsonResponse(res)
    item_list = Invest_Record.objects.all()
    startTime = request.POST.get("startTime", None)
    endTime = request.POST.get("endTime", None)
    if startTime and endTime:
        s = datetime.datetime.strptime(startTime,'%Y-%m-%d')
        e = datetime.datetime.strptime(endTime,'%Y-%m-%d')
        item_list = item_list.filter(invest_date__range=(s,e))
    amountfrom = request.POST.get("amountfrom", None)
    amountto = request.POST.get("amountto", None)
    if not amountfrom is None and not amountto is None:
        item_list = item_list.filter(invest_amount__range=(amountfrom,amountto))
    username = request.POST.get("username", None)
    if username:
        item_list = item_list.filter(user_name=username)
    
    mobile = request.POST.get("mobile", None)
    if mobile:
        item_list = item_list.filter(invest_mobile=mobile)
        
    projectname = request.POST.get("projectname", None)
    if projectname:
        item_list = item_list.filter(invest_company__contains=projectname)
    phone_set = set([])
    for item in item_list:
        phone = item.invest_mobile
        if phone and len(phone)==11:
            phone_set.add(phone)
    if len(phone_set)>0:
        phone_list = list(phone_set)
        length = len(phone_list)
        times = length/500
        treg = 0
        tnum = 0
        if length%500 > 0:
            times += 1
        for t in range(times):
            frag_list = phone_list[t*500:t*500+500]
            phones = ','.join(frag_list)
            logger.info("Sending mobile messages to users:" + phones + "; content:" + content);
            reg = send_multimsg_bydhst(phones, content)
            if reg==0:
                tnum += len(frag_list)
            else:
                treg = 1
        if treg==0:
            res['code'] = 0
            res['num'] = tnum
        else:
            res['code'] = -1
            res['res_msg'] = u"发送短信失败，实际发送数量：" + str(tnum) 
    else:
        res['code'] = 0
        res['res_msg'] = u"不存在符合条件的手机号码"
    return JsonResponse(res)