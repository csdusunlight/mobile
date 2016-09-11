'''
Created on 20160608

@author: lch
'''
import logging
from wafuli.models import UserEvent
import time as ttime
from django.core.management.base import BaseCommand
from django.db.models import Sum
from account.models import MyUser
from django.conf import settings
from decimal import Decimal
logger = logging.getLogger("wafuli")
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("******Invite_charge  is beginning*********")
        month = ttime.localtime()[1]-1 or 12
        year = ttime.localtime()[0]
        year = year-1 if month == 12 else year
        inviters = MyUser.objects.all()
        for inviter in inviters:
            num = inviter.invitees.count()
            inviter.invite_scores = num*100
            inviter.save()
            print inviter.invite_scores,inviter.scores,num
#             inviter.save(update_fields=['invite_scores',])
#             print inviter.mobile,inviter.invite_account,inviter.invite_income
        logger.info("******Invite_charge is finished*********")