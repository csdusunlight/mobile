#coding:utf-8
'''
Created on 2016年7月17日

@author: lch
'''
from django.shortcuts import render, redirect
from wafuli.models import UserEvent, AdminEvent, AuditLog, TransList, UserWelfare,\
    CouponProject, Coupon, Message
import datetime
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse, Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from account.transaction import charge_money, charge_score
import logging
from account.models import MyUser
from wafuli.data import COUPON_TYPE
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
logger = logging.getLogger('wafuli')

def deliver_coupon(request):
    admin_user = request.user
    if request.method == 'GET':
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_index'))
        else:
            return render(request, 'deliver_coupon.html', {'type_list':COUPON_TYPE})
    elif request.method == 'POST':
        result = {'code':0}
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            result['code'] = -4
            result['res_msg'] = u'请登录！'
            return JsonResponse(result)
        if not admin_user.has_admin_perms('006'):
            result['code'] = -5
            result['res_msg'] = u'您没有操作权限！'
            return JsonResponse(result)
        coupon_type = request.POST.get('selecttype')
        project_id = request.POST.get('selectproject')
        if coupon_type is None or project_id is None:
            raise Http404
        else:
            project_id = int(project_id)
            coupon_type = str(coupon_type)
        project = CouponProject.objects.get(id=project_id)
        success_count = 0
        fail_list = []
        if coupon_type == '0' or coupon_type == '1':
            select_user = request.POST.get('selectuser')
            if select_user is None:
                raise Http404
            else:
                select_user = str(select_user)
            if select_user == '1':
                for user in MyUser.objects.all():
                    Coupon.objects.create(user=user, project=project)
                    msg_content = u'您收到一张优惠券：' + project.title + u'，到期日为' + \
                        project.endtime.strftime("%Y-%m-%d") + u"，请及时使用。"
                    Message.objects.create(user=user, content=msg_content, title=u"新的优惠券");
                    success_count += 1
            elif select_user == '2':
                select_list_str = request.POST.get('users')
                if select_list_str is None:
                    raise Http404
                else:
                    select_list_str = str(select_list_str)
                select_list = select_list_str.strip().split('\n')
                user_set = set([])
                for user in select_list:
                    if user:
                        user_set.add(user)
                for username in user_set:
                    try:
                        user = MyUser.objects.get(username = username)
                        Coupon.objects.create(user=user, project=project)
                        msg_content = u'您收到一张优惠券：' + project.title + u'，到期日为' + \
                            project.endtime.strftime("%Y-%m-%d") + u"，请及时使用。"
                        Message.objects.create(user=user, content=msg_content, title=u"新的优惠券");
                    except:
                        fail_list.append(username)
                    else:
                        success_count += 1
        elif coupon_type == '2':
            select_list_str = request.POST.get('codes')
            if select_list_str is None:
                raise Http404
            else:
                select_list_str = str(select_list_str)
            select_list = select_list_str.strip().split('\n')
            code_set = set([])
            for code in select_list:
                if code:
                    code_set.add(code)
            for code in code_set:
                Coupon.objects.create(project=project, exchange_code=code)
                success_count += 1
        result.update({'succ_num':success_count, 'fail_list':fail_list})
        return JsonResponse(result)
        
def get_project_list(request):
    if not request.is_ajax():
        raise Http404
    result={'prolist':{}}
    type = request.GET.get('id', None)
    if not type:
        raise Http404
    pro_list = CouponProject.objects.filter(ctype=str(type), state='1').only('id','title')
    pro_dic={}
    for x in pro_list:
        pro_dic[str(x.id)] = x.title
    result['prolist'] = pro_dic
    return JsonResponse(result)
@csrf_exempt
def parse_file(request):
    res={'code':-9,}
    file = request.FILES.get('file')
    if not file:
        res['code'] = -2
        res['res_msg'] = u'请先选择文件！'
    else:
        try:
            res['list'] = handle_uploaded_file(file)
        except Exception, e:
            logger.info(e)
            res['code'] = -3
            res['res_msg'] = u'文件格式有误！'
        else:
            res['code'] = 0
    
    return JsonResponse(res)

def handle_uploaded_file(f):
    ret = []
    with open('./name', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    with open('./name', 'r') as file:
        for line in file:
            line = line.decode('gbk')
#             line = unicode(line, errors='ignore')
            ret.append(line.strip())
    return ret

def admin_coupon(request):
    admin_user = request.user
    if request.method == "GET":
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            return redirect(reverse('admin:login') + "?next=" + reverse('admin_coupon'))
        return render(request,"admin_coupon.html")
    if request.method == "POST":
        res = {}
        if not request.is_ajax():
            raise Http404
        if not ( admin_user.is_authenticated() and admin_user.is_staff):
            res['code'] = -1
            res['url'] = reverse('admin:login') + "?next=" + reverse('admin_coupon')
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
                translist = charge_money(event_user, '0', cash, u'优惠券兑换')
                scoretranslist = charge_score(event_user, '0', score, u'优惠券兑换')
                if translist and scoretranslist:
                    event.audit_state = '0'
                    translist.user_event = event
                    translist.save(update_fields=['user_event'])
                    scoretranslist.user_event = event
                    scoretranslist.save(update_fields=['user_event'])
                    res['code'] = 0
                    
                    project = event.content_object.project
                    msg_content = u'您提交的"' + project.title + u'"兑换申请已审核通过。'
                    Message.objects.create(user=event_user, content=msg_content, title=u"优惠券兑换审核");
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
            
            project = event.content_object.project
            msg_content = u'您提交的"' + project.title + u'"兑换申请审核未通过，原因：' + reason
            Message.objects.create(user=event_user, content=msg_content, title=u"优惠券兑换审核");
        
        if res['code'] == 0:
            admin_event = AdminEvent.objects.create(admin_user=admin_user, custom_user=event_user, event_type='10')
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
            
def get_admin_coupon_page(request):
    res={'code':0,}
    user = request.user
    if not ( user.is_authenticated() and user.is_staff):
        res['code'] = -1
        res['url'] = reverse('admin:login') + "?next=" + reverse('admin_coupon')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 10)
    state = request.GET.get("state",'1')
    projecttype = request.GET.get("projecttype",'0')
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
        item_list = item_list.filter(coupon__project__provider__contains=companyname)
        
    projectname = request.GET.get("projectname", None)
    if projectname:
        item_list = item_list.filter(coupon__project__title__contains=projectname)
        
    adminname = request.GET.get("adminname", None)
    if adminname:
        item_list = item_list.filter(audited_logs__user__username=adminname)
    if projecttype=='1':
        item_list = item_list.filter(coupon__type = '0')
    if projecttype=='2':
        item_list = item_list.filter(coupon__type = '1')
    item_list = item_list.filter(event_type='4', audit_state=state).select_related('user').order_by('time')
    
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
        coupon = con.content_object
        i = {"username":con.user.username,
             "mobile":con.user.mobile,
             "type":coupon.project.get_ctype_display(),
             "company":coupon.project.provider,
             "project":coupon.project.title,
             "mobile_sub":con.invest_account,
             "remark_sub":con.remark,
             "time_sub":con.time.strftime("%Y-%m-%d %H:%M"),
             "state":con.get_audit_state_display(),
             "admin":u'无' if con.audit_state=='1' or not con.audited_logs.exists() else con.audited_logs.first().user.username,
             "time_admin":u'无' if con.audit_state=='1' or not con.audit_time else con.audit_time.strftime("%Y-%m-%d %H:%M"),
             "amount":coupon.project.amount,
             "invest_amount":con.invest_amount,
             "invest_term":con.invest_term,
             "return_amount":u"无" if con.audit_state!='0' or not con.translist.exists() else con.translist.first().transAmount,
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