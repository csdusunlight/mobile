#coding:utf-8
'''
Created on 2016年8月29日

@author: lch
'''
import logging
from wafuli.models import Welfare
from django.core.management.base import BaseCommand
from account.models import MyUser
from django.db.models import F
import datetime
import time
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Hour-task is beginning*********")
        begin_time = time.time()
        now = datetime.datetime.now()
        start = datetime.datetime(now.year, now.month, now.day, now.hour, 0, 0)
        to = start + datetime.timedelta(hours=1)
        wels = Welfare.objects.filter(state='0', startTime__range=(start, to)).update(state='1', startTime=now)
        end_time = time.time()
        logger.info("******Hour-task is finished, time:%s*********",end_time-begin_time)