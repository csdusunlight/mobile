#coding:utf-8
'''
Created on 20161221

@author: lch
'''
from account.models import User_Envelope
from django.db.models import F
from wafuli.models import UserEvent
import random
from account.transaction import charge_money
def produce(user,n):
    obj,created = User_Envelope.objects.get_or_create(user=user)
    obj.envelope_left = F('envelope_left') + n
    obj.envelope_total = F('envelope_total') + n
    obj.save(update_fields=['envelope_total','envelope_total'])
def consume(user):
    try:
        obj = User_Envelope.objects.get(user=user)
    except:
        return -1
    else:
        if obj.envelope_left < 1:
            return -2
        obj.envelope_left = F('envelope_left') - 1
        obj.save(update_fields=['envelope_left'])
        amount = random.randint(1,20)
        event = UserEvent.objects.create(user=user, event_type='8', audit_state='1',invest_amount=amount)
        translist = charge_money(user, '0', amount, u'节日红包')
        if not translist:
            return -3
        else:
            translist.user_event = event
            translist.save(update_fields=['user_event'])
            return amount