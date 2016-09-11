
#coding:utf-8
'''
Created on 2016年8月13日

@author: lch
'''
import logging
from wafuli.models import UserEvent, ZeroPrice, Hongbao, Welfare, Baoyou
import time as ttime
from django.core.management.base import BaseCommand
from django.db.models import Sum
from account.models import MyUser
from django.conf import settings
from decimal import Decimal
from django.core.urlresolvers import reverse
from django.db.models import F
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        wels = Welfare.objects.update(startTime=F('pub_date'))
#         baoyou = Baoyou.objects.all()
#         for wel in baoyou:
#             wel.url = reverse('exp_welfare_openwindow') + '?id=' + str(wel.id)+ "&type=Welfare"
#             wel.save()
#         zero_all = ZeroPrice.objects.all()
#         for zero in zero_all:
#             wel = Hongbao.objects.create(title=zero.title,news_priority=zero.news_priority,
#                                          pub_date=zero.pub_date,view_count=zero.view_count,change_user=zero.change_user,
#                                          state=zero.state,pic=zero.pic,isonMobile=zero.isonMobile,exp_url=zero.exp_url,
#                                          exp_code=zero.exp_code,advert=zero.advert,company=zero.company,
#                                          seo_title=zero.seo_title,seo_keywords=zero.seo_keywords,
#                                          seo_description=zero.seo_description,provider=zero.provider,
#                                          time_limit=zero.time_limit,type='hongbao',strategy=zero.strategy)
#         wei_list = Welfare.objects.all()
#         for obj in wei_list:
#             obj.url = reverse('welfare', kwargs={'id': obj.pk})
#             obj.save(update_fields=['url',])
