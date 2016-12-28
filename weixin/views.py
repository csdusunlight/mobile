#coding:utf-8
from django.shortcuts import render
import hashlib
from django.http.response import HttpResponse,Http404, JsonResponse
import logging
from account.models import MyUser
logger = logging.getLogger('wafuli')
from account.varify import httpconn, verifymobilecode
from django.conf import settings
from django.contrib.auth import login as auth_login
def weixin(request):
    token = '1hblsqTsdfsdfsd'
    timestamp = str(request.GET.get('timestamp'))
    nonce = str(request.GET.get('nonce'))
    signature = str(request.GET.get('signature'))
    echostr = str(request.GET.get('echostr'))
    paralist = [token,timestamp,nonce]
    paralist.sort()
    parastr = ''.join(paralist)
    siggen = hashlib.sha1(parastr).hexdigest()
    logger.info(siggen)
    logger.info(signature) 
    if siggen==signature:
        return HttpResponse(echostr)
    else:
        raise Http404

def bind_user(request):
    if request.method == 'POST':
        result = {}
        openid = request.session['openid']
        if not openid:
            result['code'] = '3'
            result['msg'] = u'请在微信中提交'
            return JsonResponse(result)
        mobile = request.POST.get('mobile')
        telcode = request.POST.get('telcode')
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
            result['code'] = 0
            try:
                user = MyUser.objects.get(mobile=mobile)
            except MyUser.DoesNotExist:
                request.session['mobile'] = mobile
                result['url'] = "/weixin/bind-user/setpasswd/"
            else:
                user.open_id = openid
                user.save(update_fields=['open_id'])
                user.backend = 'django.contrib.auth.backends.ModelBackend'#为了略过用户名和密码验证
                auth_login(request, user)
                result['url'] = "/weixin/bind-user/success/"
        return JsonResponse(result)    
    else:
        code = request.GET.get('code','')
        if not code:
            return HttpResponse(u"微信授权失败，请稍后再试")
        url = ' https://api.weixin.qq.com/sns/oauth2/access_token'
        params = {
            'grant_type':'authorization_code',
            'appid':settings.APPID,
            'secret':settings.SECRET,
            'code':code,
        }
        json_ret = httpconn(url, params, 0)
        if 'openid' in json_ret:
            openid = json_ret['openid']
            request.session['openid'] = openid
            return render(request, 'm_bind.html')
        else:
            logger.error('Getting access_token error:' + str(json_ret) )
            return HttpResponse(u"获取token失败，请稍后再试")

def bind_user_success(request):
    return render(request, 'm_bind_success.html')
def bind_user_setpasswd(request):
    return render(request, 'm_bind_setpasswd.html')