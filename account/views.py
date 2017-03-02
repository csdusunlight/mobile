#coding:utf-8
from django.shortcuts import render, redirect
from django.http.response import Http404
from .models import MyUser, Userlogin,MobileCode
from captcha.models import CaptchaStore  
from captcha.helpers import captcha_image_url
from captcha.views import imageV, generateCap
from account.varify import verifymobilecode, sendmsg_bydhst
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.conf import settings
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login as auth_login, authenticate
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.contenttypes.models import ContentType
from account.models import UserSignIn, EmailActCode
from datetime import date, timedelta, datetime
import time as ttime
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wafuli.models import (UserEvent, Finance, Task, ExchangeRecord,
    ScoreTranlist, TransList, Coupon, Message, Commodity)
from django.db.models import Sum, Count
from .transaction import charge_money, charge_score
from account.tools import send_mail, get_client_ip
from django.db import connection
import logging
from urllib import urlencode
from wafuli.tools import get_weixin_params
from wafuli_admin.models import Invite_Rank
from app.tools import is_authenticated_app
logger = logging.getLogger('wafuli')

def user_guide(request):
    if not request.is_ajax():
        return render(request, 'registration/m_user_guide.html',)
    else:
        url = ''
        mobile = request.GET.get('mobile', '')
        is_exist = 1
        try:
            MyUser.objects.get(mobile=mobile)
        except MyUser.DoesNotExist:
             is_exist = 0
        if is_exist == 1:
            redirect_field_name=REDIRECT_FIELD_NAME
            redirect_to = request.GET.get(redirect_field_name, '')
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            url_params = {
                redirect_field_name:redirect_to,
                'mobile':mobile,
            }
            pa = urlencode(url_params)
            url = reverse('login')+'?'+pa
        else:
            url = reverse('register') + '?mobile=' + mobile
        return JsonResponse({'url':url})

def invite_accept(request):
        icode = request.GET.get('icode', '')
        return render(request, 'registration/m_invite_accept.html', {'icode':icode})
#     if not request.is_ajax():
#         return render(request, 'registration/m_user_guide.html',)
#     else:
#         url = ''
#         mobile = request.GET.get('mobile', '')
#         is_exist = 1
#         try:
#             MyUser.objects.get(mobile=mobile)
#         except MyUser.DoesNotExist:
#              is_exist = 0
#         if is_exist == 1:
#             redirect_field_name=REDIRECT_FIELD_NAME
#             redirect_to = request.GET.get(redirect_field_name, '')
#             if not is_safe_url(url=redirect_to, host=request.get_host()):
#                 redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
#             url_params = {
#                 redirect_field_name:redirect_to,
#                 'mobile':mobile,
#             }
#             pa = urlencode(url_params)
#             url = reverse('login')+'?'+pa
#         else:
#             url = reverse('register') + '?mobile=' + mobile
#         return JsonResponse({'url':url})
@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/m_login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))
    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        result = {}
        if form.is_valid():
            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            
            # Okay, security check complete. Log the user in.
            user = form.get_user()           
            auth_login(request, user)
            # anything you can add here
            user.last_login_time = user.this_login_time
            user.this_login_time = datetime.now()
            Userlogin.objects.create(user=user,)
            user.save(update_fields=["last_login_time", "this_login_time"])
            result.update(code=0, url=redirect_to)
        else:
            result.update(code=1)
        return JsonResponse(result);
    else:
        mobile = request.GET.get('mobile','')
        context = {
            'mobile':mobile,
        }
        return render(request, template_name, context)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        if not request.is_ajax():
            raise Http404
        result = {}
        telcode = request.POST.get('code', None)
        mobile = request.POST.get('mobile', None)
        password = request.POST.get('password', None)
        invite_code = request.POST.get('invite', None)
        if not (telcode and mobile and password):
            result['code'] = '3'
            result['msg'] = u'传入参数不足！'
            return JsonResponse(result)
        if MyUser.objects.filter(mobile=mobile).exists():
            result['code'] = '1'
            result['msg'] = u'该手机号码已被注册，请直接登录！'
            return JsonResponse(result)
        ret = verifymobilecode(mobile,telcode)
        if ret != 0:
            result['code'] = '2'
            if ret == -1:
                result['msg'] = u'请先获取手机验证码'
            elif ret == 1:
                result['msg'] = u'手机验证码输入错误！'
            elif ret == 2:
                result['msg'] = u'手机验证码已过期，请重新获取'
            return JsonResponse(result)
        inviter = None
        if invite_code:
            try:
                inviter = MyUser.objects.get(invite_code=invite_code)
            except MyUser.DoesNotExist:
                result['code'] = '2'
                result['msg'] = u'该邀请码不存在，请检查'
                return JsonResponse(result)
        try:
            username = 'm' + str(mobile)
            user = MyUser(mobile=mobile, username=username, inviter=inviter)
            user.set_password(password)
            user.save()
            logger.info('Creating User:' + mobile + ' succeed!')
            # 注册奖励2元
            reg_award = 200
            trans = charge_money(user, '0', reg_award, u"注册奖励")
            if trans:
                logger.debug('Registering Award money is successfully payed!')
            else:
                logger.debug('Registering Award money is failed to pay!!!')
        except Exception,e:
            logger.error(e)
            result['code'] = '4'
            result['msg'] = u'创建用户失败！'
        else:
            result['code'] = '0'
            # 邀请人奖励10积分
            if inviter:
                invite_award_scores = 10
                inviter.invite_scores += invite_award_scores
                translist = charge_score(inviter, '0', invite_award_scores, u"邀请奖励")
                if translist:
                    logger.debug('Inviting Award scores is successfully payed!')
                    inviter.save(update_fields=['invite_scores'])
                else:
                    logger.debug('Inviting Award scores is failed to pay!!!')
            try:
                userl = authenticate(username=username, password=password)
                auth_login(request, userl)
                user.this_login_time = datetime.now()
                Userlogin.objects.create(user=userl,)
            except:
                pass
        return JsonResponse(result)
    else:
        mobile = request.GET.get('mobile','')
        icode = request.GET.get('icode','')
        hashkey = CaptchaStore.generate_key()
        codimg_url = captcha_image_url(hashkey)
        icode = request.GET.get('icode','')
        context = {
            'hashkey':hashkey, 
            'codimg_url':codimg_url, 
            'icode':icode,
            'mobile':mobile,
        }
        return render(request,'registration/m_register.html', context)
@login_required
def get_nums(request):
    coupon_num = Coupon.objects.filter(user=request.user, is_used=False).count()
    message_num = Message.objects.filter(user=request.user, is_read=False).count()
    result = {'coupon_num':coupon_num,'message_num':message_num,}
    return JsonResponse(result)
def verifyemail(request):
    emailv = request.GET.get('email', None)
    users = None
    code = '0' # is used
    if emailv:
        users = MyUser.objects.filter(email=emailv)
        if not users.exists():
            code = '1'
    
    result = {'code':code,}
    return JsonResponse(result)
def verifymobile(request):
    mobilev = request.GET.get('mobile', None)
    users = None
    code = '0' # is used
    if mobilev:
        users = MyUser.objects.filter(mobile=mobilev)
        if not users.exists():
            code = '1'    
    result = {'code':code,}
    return JsonResponse(result)
def verifyusername(request):
    namev = request.GET.get('username', None)
    users = None
    code = '0' # is used
    if namev:
        users = MyUser.objects.filter(username=namev)
        if not users.exists():
            code = '1'
    result = {'code':code,}
    return JsonResponse(result)
def verifyinviter(request):
    invite_code = request.GET.get('invite', None)
    code = '0' # not exist
    if invite_code:
        users = MyUser.objects.filter(invite_code=invite_code)
        if users.exists():
            code = '1'
    result = {'code':code,}
    return JsonResponse(result)
@csrf_exempt
def callbackby189(request):
    rand_code = request.POST.get('rand_code', None)
    identifier = request.POST.get('identifier', None)
    code = '0' # is used
    if not rand_code or not identifier:
        logger.error('where is it???')
        code = '1'
    else:
        try:
            MobileCode.objects.create(identifier=identifier, rand_code=rand_code)
        except:
            code = '1'
        else:
            code = '0'        
    result = {'res_code':code,}
    return JsonResponse(result)

def phoneImageV(request):
    if not request.is_ajax():
        raise Http404
    action = request.GET.get('action', None)
    result = {'code':-1, 'message':'error!'}
    phone = ''
    if action=='register':
        phone = request.GET.get('phone', None)
        hashkey = request.GET.get('hashkey', None)
        response = request.GET.get('response', None)
        if not (phone and hashkey):
            return JsonResponse(result)
        ret = imageV(hashkey, response)
        if ret != 0:
            result['code'] = 1
            result['message'] = u'图形验证码输入错误！'
            result.update(generateCap())
            return JsonResponse(result)
        users = MyUser.objects.filter(mobile=phone)
        if users.exists():
            result['code'] = 1
            result['message'] = u'该手机号码已被注册，请直接登录！'
            result.update(generateCap())
            return JsonResponse(result)
    elif action=='reset_password':
        phone = request.GET.get('phone', None)
        hashkey = request.GET.get('hashkey', None)
        response = request.GET.get('response', None)
        if not (phone and hashkey):
            return JsonResponse(result)
        ret = imageV(hashkey, response)
        if ret != 0:
            result['code'] = 1
            result['message'] = u'图形验证码输入错误！'
            result.update(generateCap())
            return JsonResponse(result)
        users = MyUser.objects.filter(mobile=phone)
        if not users.exists():
            result['code'] = 1
            result['message'] = u'该手机号码尚未注册！'
            result.update(generateCap())
            return JsonResponse(result)
    elif action=="change_zhifubao":
        if not request.user.is_authenticated() and not is_authenticated_app(request):
            result['code'] = 1
            result['message'] = u"尚未登录"
            return JsonResponse(result)
        phone = request.user.mobile
    elif action=="bind_weixin":
        phone = request.GET.get('phone', None)
        openid = request.session.get('openid',None)
        if not openid:
            result['code'] = 1
            result['message'] = u"请在微信中打开网页"
            return JsonResponse(result)
    stamp = str(phone)
    lasttime = request.session.get(stamp, None)
    now = int(ttime.time())
    if lasttime:
        dif = now - int(lasttime)
        if dif < 60:
            result['code'] = 2
            result['message'] = u'请不要频繁提交！'
            result.update(generateCap())
            return JsonResponse(result)
    today = date.today()
    remote_ip = get_client_ip(request)
    count_ip = MobileCode.objects.filter(remote_ip=remote_ip, create_at__gt=today).count()
    if count_ip >= 30:
        result['code'] = 3
        result['message'] = u'该IP当日发送短信请求已超上限，请明日再来！'
        result.update(generateCap())
        return JsonResponse(result)
    count_mobile = MobileCode.objects.filter(mobile=phone, create_at__gt=today).count()
    if count_mobile >= 5:
        result['code'] = 3
        result['message'] = u'该手机号当日短信发送请求已超上限，请明日再来！'
        result.update(generateCap())
        return JsonResponse(result)
    ret = sendmsg_bydhst(phone)
    if ret:
        logger.info('Varifing code has been send to:' + phone)
        result['code'] = 0
        MobileCode.objects.create(mobile=phone,rand_code=ret,remote_ip=remote_ip)
        request.session[stamp] = now
    else:
        logger.error('Sending Varifing code to ' + phone + ' is failed!!!')
        result['code'] = 1
        result['message'] = u"发送验证码失败！"
        result.update(generateCap())
    return JsonResponse(result)

@login_required
def account(request):
    ref_url = request.META.get('HTTP_REFERER',"")
#     anyhongbao = User_Envelope.objects.filter(user=request.user,envelope_left__gt=0).exists()
    anymessage = Message.objects.filter(user=request.user,is_read=False).exists()
    context={'anymessage':anymessage}
    if 'next=' in ref_url:
        context.update(back=True)
    signin_last = UserSignIn.objects.filter(user=request.user).first()
    isSigned = False
    signed_conse_days = 0
    if signin_last and signin_last.date == date.today():
        isSigned = True
    context.update(isSigned=isSigned)
    return render(request, 'account/m_account_index.html', context)
@login_required
def account_settings(request):
    return render(request, 'account/m_account_settings.html', )
@login_required
def signin(request):
    user = request.user
    signin_last = UserSignIn.objects.filter(user=user).first()
    if request.is_ajax():
        result={'code':-1, 'url':''}
        if signin_last and signin_last.date == date.today():
            result['code'] = 1
        else:
            signed_conse_days = 1
            if signin_last and signin_last.date == date.today() - timedelta(days=1):
                signed_conse_days += signin_last.signed_conse_days
            UserSignIn.objects.create(user=request.user, date=date.today(), signed_conse_days=signed_conse_days)
            charge_score(request.user, '0', 5, u"签到奖励")
            if signed_conse_days%7 == 0:
                charge_score(request.user, '0', 20, u"连续签到7天奖励")
            result['code'] = 0
        return JsonResponse(result)
    else:
        flag = None
        today = date.today()
        if signin_last and signin_last.date == today:
            flag = 0
        else:
            flag = 1
            signed_conse_days = 1
            if signin_last and signin_last.date == today - timedelta(days=1):
                signed_conse_days += signin_last.signed_conse_days
            UserSignIn.objects.create(user=user, date=today, signed_conse_days=signed_conse_days)
            charge_score(user, '0', 5, u"签到奖励")
            if signed_conse_days%7 == 0:
                charge_score(user, '0', 20, u"连续签到7天奖励")
        context = {'flag':flag}
        ref_url = request.META.get('HTTP_REFERER',"")
        if 'next=' in ref_url:
            context.update({'back':True})
        return render(request, 'account/m_signin.html',context)
def signin_record(request):
    if not request.user.is_authenticated() and not is_authenticated_app(request):
        raise Http404
    today = date.today()
    first_day_of_month = today - timedelta(today.day-1)
    sign_days = UserSignIn.objects.filter(user=request.user,date__gte=first_day_of_month).values('date');
    records = []
    for day in sign_days:
        records.append(day.get('date').day);
    return JsonResponse(records,safe=False)
@login_required
def welfare(request):
    ttype = ContentType.objects.get_for_model(Task)
    ftype = ContentType.objects.get_for_model(Finance)
    tcount_u = UserEvent.objects.filter(user=request.user.id, content_type = ttype.id).count()
    fcount_u = UserEvent.objects.filter(user=request.user.id, content_type = ftype.id).count()
    statis = {'tcount_u':tcount_u,'fcount_u':fcount_u }
    return render(request, 'account/m_account_welfare.html', {'statis':statis})


def get_user_welfare_json(request):
    if not request.is_ajax():
        raise Http404
    res={'code':0,}
    if not request.user.is_authenticated() and not is_authenticated_app(request):
        raise Http404
    type = request.GET.get("type", 0)
    count = request.GET.get("count", 0)
    try:
        count = int(count)
        type = int(type)
    except ValueError:
        count = 0
        type = 0
    item_list = []
    if type == 0:
        etype = ContentType.objects.get_for_model(Task)
    else:
        etype = ContentType.objects.get_for_model(Finance)
        
    start = 12*count
    item_list = UserEvent.objects.filter(user=request.user, content_type = etype)[start:start+12]
    data = []
    for con in item_list:
        reason = con.remark
        if con.audit_state == '2':
            log = con.audited_logs.first()
            if log:
                reason = log.reason
        i = {"title":con.content_object.title,
             "username":con.invest_account,
             "time":con.time.strftime("%Y-%m-%d"),
             "state":con.get_audit_state_display(),
             "state_int":con.audit_state,
             "reason":reason
             }
        data.append(i)
    return JsonResponse(data, safe=False)

@login_required
def score(request):
    return render(request, 'account/m_account_score.html', {})

def score_json(request):
    user = request.user
    res={'code':0,}
    if not user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('user_guide') + "?next=" + reverse('account_score')
        return JsonResponse(res)
    count = int(request.GET.get('count', 0))
    type = str(request.GET.get('type', '0'))
    start = 6*count
    item_list = ScoreTranlist.objects.filter(user=request.user, transType=type)[start:start+6]
    data = []
    for con in item_list:      
        i = {"reason":con.reason,
             "amount":con.transAmount,
             "date":con.time.strftime("%Y-%m-%d"),
             }
        if type == '1':
            event = con.user_event
            if event and event.event_type == '3':
                state = event.get_audit_state_display()
            else:
                state = u"无"
            i.update({"state":state})
        data.append(i)
    return JsonResponse(data, safe=False)

@login_required
def security(request):
    return render(request, 'account/account_security.html', {})

def change_pay_password(request):
    if not request.is_ajax():
        raise Http404
    result={'code':-1, 'url':'asd'}
    if not request.user.is_authenticated():
        result['code'] = 1
        result['url'] = reverse('login') + "?next=" + reverse('account_security')
        return JsonResponse(result)
    init_password = request.POST.get("initp", '')
    new_password = request.POST.get("newp", '')
    type = request.POST.get("type", '')
    if not (init_password and new_password and type):
        result['code'] = -1
        return JsonResponse(result)
    user = request.user
    vari = False
    if type == 'set':
        vari = user.check_password(init_password)
    elif type == 'change':
        vari = user.check_pay_password(init_password)
    if vari:
        user.set_pay_password(new_password)
        user.save(update_fields=["pay_password"])
        result['code'] = 0
    else:
        result['code'] = 2
    return JsonResponse(result)
def active_email(request):
    result={'code':-1, 'url':'asd'}
    if request.is_ajax():
        user = request.user
        if not user.is_authenticated():
            result['code'] = 1
            result['url'] = reverse('login') + "?next=" + reverse('active_email')
            return JsonResponse(result)
        code = send_mail(user.email, user.pk)
        if code:
            EmailActCode.objects.update_or_create(email=user.email, defaults={'rand_code':code})
            result['code'] = 0
        else:
            result['code'] = 2
        return JsonResponse(result)
    elif request.method == 'GET':
        code = request.GET.get("code", '')
        try:
            obj = EmailActCode.objects.get(rand_code=code)
            user = MyUser.objects.get(email=obj.email)
            user.is_email_authenticated = True
            user.save(update_fields=["is_email_authenticated"])
            return redirect('account_security')
        except Exception, e:
            logger.error(str(e))
            raise Http404

@login_required
def bind_zhifubao(request):
    if request.method == 'POST':
        if not request.is_ajax():
            raise Http404
        result={}
        user = request.user
        zhifubao = request.POST.get("account", '')
        zhifubao_name = request.POST.get("name", '')
        if not user.zhifubao:
            user.zhifubao = zhifubao
            user.zhifubao_name = zhifubao_name
            user.save(update_fields=["zhifubao","zhifubao_name",])
            result['code'] = 0
            result['msg'] = u'绑定成功！'
        else:
           result['code'] = 3 
           result['msg'] = u'您已绑定过支付宝！'
        return JsonResponse(result)
    else:
        return render(request, 'account/m_account_bind_zhifubao.html')

@login_required
def change_zhifubao(request):
    if request.method == 'POST':
        if not request.is_ajax():
            raise Http404
        result={}
        user = request.user
        zhifubao = request.POST.get("account", '')
        zhifubao_name = request.POST.get("name", '')
        telcode = request.POST.get("telcode", '')
        ret = verifymobilecode(user.mobile,telcode)
        if ret != 0:
            result['code'] = 2
            if ret == -1:
                result['msg'] = u'请先获取手机验证码！'
            elif ret == 1:
                result['msg'] = u'手机验证码输入错误！'
            elif ret == 2:
                result['msg'] = u'手机验证码已过期，请重新获取'
            return JsonResponse(result)
        else:
            user.zhifubao = zhifubao
            user.zhifubao_name = zhifubao_name
            user.save(update_fields=["zhifubao","zhifubao_name",])
            result['code'] = 0
            result['msg'] = u"支付宝账号更改成功！"
        return JsonResponse(result)
    else:
        return render(request, 'account/m_account_change_zhifubao.html')

@login_required
def charge(request):
    return render(request, 'account/m_account_charge.html', {})

def charge_json(request):
    user = request.user
    res={'code':0,}
    if not user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('user_guide') + "?next=" + reverse('account_charge')
        return JsonResponse(res)
    count = int(request.GET.get('count', 0))
    type = str(request.GET.get('type', '0'))
    start = 6*count
    item_list = TransList.objects.filter(user=request.user, transType=type)[start:start+6]
    data = []
    for con in item_list:      
        i = {"reason":con.reason,
             "amount":con.transAmount,
             "date":con.time.strftime("%Y-%m-%d"),
             }
        if type == '1':
            event = con.user_event
            if event:
                state = event.get_audit_state_display()
            else:
                state = u"无"
            i.update({"state":state,})
        data.append(i)
    return JsonResponse(data, safe=False)

@login_required
def withdraw(request):
    if request.method == 'GET':
        hashkey = CaptchaStore.generate_key()
        codimg_url = captcha_image_url(hashkey)
        return render(request,'account/m_account_withdraw.html')
    elif request.method == 'POST':
        user = request.user
        result = {'code':-1, 'msg':''}
        withdraw_amount = request.POST.get("amount", None)
        if not withdraw_amount:
            result['code'] = 3
            result['msg'] = u'传入参数不足！'
            return JsonResponse(result)
        try:
            withdraw_amount = int(withdraw_amount)
        except ValueError:
            result['code'] = -1
            result['msg'] = u'参数不合法！'
            return JsonResponse(result)
        if withdraw_amount < 1000 or withdraw_amount > user.balance:
            result['code'] = -1
            result['msg'] = u'余额不足！'
            return JsonResponse(result)
        if not user.zhifubao or not user.zhifubao_name:
            result['code'] = -1
            result['msg'] = u'请先绑定支付宝！'
        else:
            translist = charge_money(user, '1', withdraw_amount, u'提现')
            if translist:
                event = UserEvent.objects.create(user=user, event_type='2', invest_account=user.zhifubao,
                            invest_amount=withdraw_amount, audit_state='1')
                translist.user_event = event
                translist.save(update_fields=['user_event'])
                result['code'] = 0
                result['msg'] = u'提交成功，请耐心等待审核通过！'
            else:
                result['code'] = -2
                result['msg'] = u'提交失败！'
        return JsonResponse(result)

@login_required
def exchange(request):
    return render(request, 'account/m_account_exchange.html', {})
def exchange_morescore(request):
    return render(request, 'm_exchange_morescore.html', {})
def exchange_introduction(request):
    return render(request, 'm_exchange_introduction.html', {})
def exchange_questions(request):
    return render(request, 'm_exchange_questions.html', {})


def commodity_json(request):
    count = int(request.GET.get('count', 0))
    data = []
    count = int(count)
    start = 12*count
    good_list = Commodity.objects.all()[start:start+12]
    for good in good_list:
        data.append({
            'id':good.id,
            'picurl':good.pic.url,
            'name':good.name,
            'price':good.price,
        })
    return JsonResponse(data,safe=False)

@login_required
def coupon(request):
    user = request.user
    coupons = user.user_coupons.filter(is_used=False)
    dict = {
        'cash_num' : coupons.filter(project__ctype='0').count(),
        'interest_num' : coupons.filter(project__ctype='1').count(),
        'exc_num' : coupons.filter(project__ctype='2').count()
    }
    return render(request, 'account/m_account_coupon.html', {'dict':dict})

def user_coupon_json(request):
    user = request.user
    if not user.is_authenticated() and not is_authenticated_app(request):
        res={'code':-1,}
        return JsonResponse(res)
    count = int(request.GET.get('count', 0))
    type = str(request.GET.get("type", ''))
    #移动端顺序是使用0、现金1、加息2，数据库是使用2、现金0、加息1
    if type == '0':
        type = '2'
    elif type == '1':
        type = '0'
    elif type == '2':
        type = '1'
    data = []
    count = int(count)
    start = 6*count
    try:
        count = int(count)
    except ValueError:
        count = 0
    item_list = Coupon.objects.filter(user=request.user,project__ctype=type).select_related('project').order_by('-time')[start:start+6]
    for con in item_list:
        project = con.project
        i = {"title":project.title,
             "amount":project.amount,
             "introduction":project.introduction,
             "url":project.exp_url_mobile,
             'endtime':project.endtime,
             'id':con.id,
             'code':con.exchange_code,
             'imgurl':project.pic.url,
             'is_used':con.is_used,
        }
        data.append(i)
    return JsonResponse(data,safe=False)
def get_user_coupon_exchange_detail(request):
    if not request.user.is_authenticated() and not is_authenticated_app(request):
        res={'code':-1,}
        return JsonResponse(res)
    count = int(request.GET.get('count', 0))
    type = request.GET.get("type", '')
    data = []
    count = int(count)
    start = 12*count
    item_list = UserEvent.objects.filter(user=request.user,event_type='4')[start:start+12]
    data = []
    for con in item_list:
        coupon = con.content_object
        i = {"title":coupon.project.title,
             "amount":coupon.project.amount,
             "account":con.invest_account,
             "state":con.get_audit_state_display(),
             'remark':con.remark,
             'time':con.time.strftime("%Y-%m-%d %H:%M:%S"),
             'type':coupon.project.get_ctype_display()
        }
        data.append(i)
    return JsonResponse(data,safe=False)

@csrf_exempt
def useCoupon(request):
    if not request.user.is_authenticated() and not is_authenticated_app(request):
        res={'code':-1,'msg':u"尚未登录"}
        return JsonResponse(res)
    coupon_id = request.POST.get('id', None)
    telnum = request.POST.get('telnum', None)
    remark = request.POST.get('remark', '')
    coupon_id = int(coupon_id)
    coupon = Coupon.objects.get(pk=coupon_id)
    code=''
    msg=''
    if coupon.is_used:
        code = '2'
        msg = u'该优惠券已兑换，请查看兑换记录！'
    else:
        events = UserEvent.objects.filter(invest_account=telnum, event_type='4',)
        if events.exists():
            pro_list = []
            project = coupon.project
            for eve in events:
                cou = eve.content_object
                pro_list.append(cou.project)
            if project in pro_list:
                code = '2'
                msg = u'该账号已领取奖励，请不要重复提交！'
    if code!='2':
        UserEvent.objects.create(user=request.user, event_type='4', invest_account=telnum,
                     content_object=coupon, audit_state='1',remark=remark,)
        code = '1'
        msg = u'提交成功，请查看兑换记录！'
        coupon.is_used = True
        coupon.save(update_fields=['is_used'],)
    result = {'code':code, 'msg':msg}
    return JsonResponse(result)

def get_user_message_page(request):
    res={'code':0,}
    if not request.user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('login') + "?next=" + reverse('account_coupon')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 5)
    try:
        size = int(size)
    except ValueError:
        size = 5
    if not page or size <= 0:
        raise Http404
    item_list = Message.objects.filter(user=request.user)
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
             'content':con.content,
             'id':con.id,
             'code':con.time.strftime("%Y-%m-%d"),
             'state':"on" if con.is_read else ""
        }
        data.append(i)
    if data:
        res['code'] = 1
    res["pageCount"] = paginator.num_pages
    res["recordCount"] = item_list.count()
    res["data"] = data
    return JsonResponse(res)

@login_required
def invite(request):
    inviter = request.user
    if request.method == 'GET':
        withdraw_thismonth = UserEvent.objects.filter(user__inviter=inviter, event_type='2',
                    audit_state='0',audit_time__year=ttime.localtime()[0],audit_time__month=ttime.localtime()[1]).\
                    aggregate(sumofwith=Sum('invest_amount'))
        acc_count = inviter.invitees.count()
        acc_with_count = UserEvent.objects.filter(user__inviter=inviter, event_type='2',
                    audit_state='0').values('user__mobile').distinct().order_by().count()
        this_month_award = float(withdraw_thismonth.get('sumofwith') or 0)*settings.AWARD_RATE
        this_month_award = int(this_month_award)
        statis = {
            'left_award':inviter.invite_account,
            'accu_invite_award':inviter.invite_income,   
            'accu_invite_scores':inviter.invite_scores,
            'acc_count':acc_count,
            'acc_with_count':acc_with_count,
            'this_month_award':this_month_award, 
        }
#         if wel.type != "baoyou":
        url = request.get_full_path()#reverse('user_guide')
        weixin_params = get_weixin_params(url)
        return render(request,'account/m_account_invite.html', {'statis':statis, 'weixin_params':weixin_params})
    elif request.method == 'POST':
        result = {'code':-1, 'msg':''}
        left_award = inviter.invite_account
        if left_award == 0:
            result['msg'] = u'邀请奖励结余为0'
        else:
            translist = charge_money(inviter, '0', left_award, u'邀请奖励')
            if translist:
                inviter.invite_account = 0
                inviter.save(update_fields=['invite_account'])
                event = UserEvent.objects.create(user=inviter, event_type='5',
                            invest_amount=left_award, audit_state='1')
                translist.user_event = event
                translist.save(update_fields=['user_event'])
                result['code'] = 0
            else:
                result['code'] = -2
                result['msg'] = u'操作失败，请联系客服！'
        return JsonResponse(result)
    
def get_user_invite_page(request):
    if not request.is_ajax():
        raise Http404
    user = request.user
    res={'code':0,}
    if not user.is_authenticated():
        res['code'] = -1
        res['url'] = reverse('login') + "?next=" + reverse('account_invite')
        return JsonResponse(res)
    page = request.GET.get("page", None)
    size = request.GET.get("size", 6)
    filter = request.GET.get("filter",0)
    try:
        size = int(size)
    except ValueError:
        size = 6
    try:
        filter = int(filter)
    except ValueError:
        filter = 0
    if not page or size <= 0 or filter < 0 or filter > 2:
        raise Http404

    data = []
    if filter == 0:
        invitees = user.invitees.all()
        paginator = Paginator(invitees, size)
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        for con in contacts:
            reg = UserEvent.objects.filter(user=con, event_type='2',audit_state='0').exists()
            mobile = con.mobile
            if len(mobile)==11:
                mobile = mobile[0:3] + '****' + mobile[7:]
            i = {
                 "mobile":mobile,
                 "time":con.date_joined.strftime("%Y-%m-%d %H:%M"),
                 "is_bind":u'是' if con.zhifubao else u'否',
                 "is_with":u'是' if reg else u'否',
             }
            data.append(i)
        if data:
            res['code'] = 1
        res["pageCount"] = paginator.num_pages
        res["recordCount"] = invitees.count()
    elif filter == 1:
        events = UserEvent.objects.filter(user__inviter=user, event_type='2', audit_state='0')
        paginator = Paginator(events, size)
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        for con in contacts:
            take_award = float(con.invest_amount)*settings.AWARD_RATE
            take_award = int(take_award)
            i = {
                 "mobile":con.user.mobile,
                 "time":con.audit_time.strftime("%Y-%m-%d %H:%M"),
                 "amount":con.invest_amount,
                 "take":take_award,
             }
            data.append(i)
        if data:
            res['code'] = 1
        res["pageCount"] = paginator.num_pages
        res["recordCount"] = events.count()
    elif filter == 2:
        select = {'month': connection.ops.date_trunc_sql('month', 'time')}
        withdraw_list = UserEvent.objects.filter(user__inviter=user, event_type='2',
                audit_state='0',).extra(select=select)\
                .values('month').annotate(cou=Count('user',distinct=True),sumofwith=Sum('invest_amount')).order_by('-month',)
        paginator = Paginator(withdraw_list, size)
        
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        for con in contacts:
            take_award = float(con['sumofwith'] or 0)*settings.AWARD_RATE
            take_award = int(take_award)
            i = {
                 "month":str(con['month'])[0:7],
                 "amount":con['sumofwith'] or 0,
                 "cou":con['cou'],
                 "take":take_award,
                 "score":con['cou']*100,
             }
            data.append(i)
        if data:
            res['code'] = 1
        res["pageCount"] = paginator.num_pages
        res["recordCount"] = withdraw_list.count()
    res["data"] = data
    return JsonResponse(res)

@csrf_exempt
def password_reset(request):
    if request.method == 'POST':
        if not request.is_ajax():
            raise Http404
        result = {}
        telcode = request.POST.get('code', None)
        mobile = request.POST.get('mobile', None)
        password = request.POST.get('password', None)
        if not (telcode and mobile and password):
            result['code'] = '3'
            result['msg'] = u'传入参数不足！'
            return JsonResponse(result)
        user = None
        try:
            user = MyUser.objects.get(mobile=mobile)
        except:
            result['code'] = '1'
            result['msg'] = u'该手机号码尚未注册！'
            return JsonResponse(result)
        ret = verifymobilecode(mobile,telcode)
        if ret != 0:
            result['code'] = '2'
            if ret == -1:
                result['msg'] = u'请先获取手机验证码'
            elif ret == 1:
                result['msg'] = u'手机验证码输入错误！'
            elif ret == 2:
                result['msg'] = u'手机验证码已过期，请重新获取'
        else:
            user.set_password(password)
            user.save(update_fields=["password"])
            result['code'] = 0
            result['msg'] = u'密码重置成功！'
        return JsonResponse(result)
    else:
        hashkey = CaptchaStore.generate_key()
        codimg_url = captcha_image_url(hashkey)
        context = {
            'hashkey':hashkey, 
            'codimg_url':codimg_url, 
        }
        return render(request,'m_password_reset.html',context)

@login_required
def password_change(request):
    if request.method == 'POST':
        if not request.is_ajax():
            raise Http404
        result={'code':-1, 'msg':''}
        init_password = request.POST.get("initp", '')
        new_password = request.POST.get("newp", '')
        if not (init_password and new_password):
            result['code'] = -1
            result['msg'] = u'请输入密码！'
            return JsonResponse(result)
        user = request.user
        if not user.check_password(init_password):
            result['code'] = 2
            result['msg'] = u'当前密码输入错误！'
        else:
            user.set_password(new_password)
            user.save(update_fields=["password"])
            userl = authenticate(username=user.mobile, password=new_password)
            auth_login(request, userl)
            result['code'] = 0
            result['msg'] = u'密码修改成功！'
        return JsonResponse(result)
    else:
        return render(request,'account/m_account_change_password.html')
    
@login_required
def message_json(request):
    count = int(request.GET.get('count', 0))
    if not request.is_ajax():
        logger.warning("Experience refused no-ajax request!!!")
        raise Http404
    data = []
    start = 10*count
    msg_list = Message.objects.filter(user=request.user).order_by('-time')[start:start+10]
    for msg in msg_list:
        data.append({
            'title':msg.title,
            'url':'/account/message/' + str(msg.id),
            'content':msg.content,
            'time':msg.time.strftime('%Y-%m-%d %H:%M:%S'),
            'is_read':msg.is_read
        })
    return JsonResponse(data,safe=False)

@login_required
def message(request, id=None):
    if id is None:
        return render(request,'account/m_account_message.html')
    else:
        id = int(id)
        msg = None
        try:
            msg = Message.objects.get(id=id,user=request.user)
        except Message.DoesNotExist:
            raise Http404(u"该消息不存在")
        msg.is_read = True
        msg.save(update_fields=['is_read',])
        context={'content':msg.content}
        return render(request, 'account/m_detail_message.html', context)