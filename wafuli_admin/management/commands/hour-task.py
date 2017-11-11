#coding:utf-8
'''
Created on 2016年8月29日

@author: lch
'''
import logging
from wafuli.models import Welfare
from django.core.management.base import BaseCommand
from account.models import MyUser, WeiXinUser
from django.db.models import F
import datetime
import time
from account.varify import httpconn
from wafuli_admin.models import Dict
from django.conf import settings
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Hour-task is beginning*********")
        begin_time = time.time()
        now = datetime.datetime.now()
        start = datetime.datetime(now.year, now.month, now.day, now.hour, 0, 0)
        to = start + datetime.timedelta(hours=1)
        wels = Welfare.objects.filter(state='0', startTime__range=(start, to)).update(state='1', startTime=now)
        
        access_token = update_accesstoken()
        update_jsapi_ticket(access_token)
        sendTemplate(access_token)
        end_time = time.time()
        logger.info("******Hour-task is finished, time:%s*********",end_time-begin_time)
        
def update_accesstoken():
    url = 'https://api.weixin.qq.com/cgi-bin/token'
    params = {
        'grant_type':'client_credential',
        'appid':settings.APPID,
        'secret':settings.SECRET,
    }
    json_ret = httpconn(url, params, 0)
    if 'access_token' in json_ret and 'expires_in' in json_ret:
        access_token = json_ret['access_token']
        now = int(time.time())
        expire_stamp = now + json_ret['expires_in']
        defaults={'value':access_token, 'expire_stamp':expire_stamp}
        Dict.objects.update_or_create(key='access_token', defaults=defaults)
        return access_token
    else:
        logger.error('Getting access_token error:' + str(json_ret) )
        return ''
def update_jsapi_ticket(access_token):
    url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket'
    params = {
        'type':'jsapi',
        'access_token':access_token,
    }
    json_ret = httpconn(url, params, 0)
    if 'ticket' in json_ret and 'expires_in' in json_ret:
        jsapi_ticket = json_ret['ticket']
        now = int(time.time())
        expire_stamp = now + json_ret['expires_in']
        defaults={'value':jsapi_ticket, 'expire_stamp':expire_stamp}
        Dict.objects.update_or_create(key='jsapi_ticket', defaults=defaults)
    else:
        logger.error('Getting access_token error:' + str(json_ret) )

def sendTemplate(access_token):
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=' + access_token
    kwarg = {}
    kwarg.update(access_token=access_token, template_id='XKGoq0xWvXrg5alO_3pc4f4F5wKR7EDnfvzPoUlh-wY')
    to_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx76aa03447c27f99d&redirect_uri=http%3A%2F%2Ftest.wafuli.cn%2Fweixin%2Fbind-user%2F&response_type=code&scope=snsapi_userinfo"
    kwarg.update(url=to_url, topcolor="#FF0000")
    wusers = WeiXinUser.objects.all()
    for wu in wusers:
        openid = wu.openid
        data = {'user':{'value':wu.user.username, 'color':"#173177"},}
        kwarg.update(data=data, touser=openid)
        ret = httpconn(url, kwarg, 1)
        logger.info(msg)
    