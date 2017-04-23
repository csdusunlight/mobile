#coding:utf-8
'''
Created on 2017年4月23日

@author: lch
'''
from account.transaction import charge_money
from wafuli.models import Message
VIP_BONUS = {
    0:{'finance':1, 'task':1, 'money':0,},
    1:{'finance':1.01, 'task':1.010, 'money':500,},
    2:{'finance':1.02, 'task':1.12, 'money':3000,},
    3:{'finance':1.03, 'task':1.14, 'money':20000,},
    4:{'finance':1.04, 'task':1.16, 'money':80000,},
    5:{'finance':1.05, 'task':1.18, 'money':120000,},
}
VIP_AMOUNT = {0:0, 1:10000, 2:100000, 3:1000000, 4:5000000, 5:10000000,}
def get_vip_bonus(user, amount, type):
    level = user.level
    return int(amount*VIP_BONUS[level][type])
def vip_judge(user, with_amount):
    level = user.level
    total = user.with_total
    ntotal = user.with_total + with_amount
    user.with_total = ntotal
    keys = sorted(VIP_AMOUNT.keys())
    for key in keys:
        value = VIP_AMOUNT[key]
        if ntotal >= value and total < value:
            if key > level:
                user.level = key
                charge_money(user, '0', VIP_BONUS[key]['money'], u'VIP升级奖励')
                msg_content = u'恭喜您的会员等级提升为VIP' + str(key) + u'！'
                Message.objects.create(user=user, content=msg_content, title=u"会员升级")
    user.save()
    