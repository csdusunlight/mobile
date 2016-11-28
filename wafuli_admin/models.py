#coding:utf-8
from django.db import models
from account.models import MyUser
class DayStatis(models.Model):
    date = models.DateField(u"日期", primary_key=True)
    new_reg_num = models.PositiveIntegerField(u"新注册人数", default=0)
    active_num = models.PositiveIntegerField(u"活跃人数", default=0)
    with_amount = models.IntegerField(u'提现成功金额', default=0)
    with_num = models.PositiveIntegerField(u"提现成功人数", default=0)
    ret_amount = models.IntegerField(u'返现金额', default=0)
    ret_scores = models.PositiveIntegerField(u"赠送积分", default=0)
    ret_num = models.PositiveIntegerField(u"返现人数", default=0)
    coupon_amount = models.IntegerField(u'红包兑现金额', default=0)
    exchange_num = models.PositiveIntegerField(u"兑换人数", default=0)
    exchange_scores = models.PositiveIntegerField(u"积分兑换", default=0)
    new_wel_num = models.PositiveIntegerField(u"今日上线福利", default=0)
    lottery_people = models.PositiveIntegerField(u"今日抽奖人数", default=0)
    lottery_num = models.PositiveIntegerField(u"今日抽奖次数", default=0)
    def __unicode__(self):
        return self.date.strftime("%Y-%m-%d")
    class Meta:
        ordering = ['-date']

class RecommendRank(models.Model):
    user = models.OneToOneField(MyUser,related_name="rank_of")
    rank = models.PositiveIntegerField(u"排名", default=100)
    sub_num = models.PositiveIntegerField(u"福利提交数", default=0)
    acc_num = models.PositiveIntegerField(u"福利采纳数", default=0)
    award = models.IntegerField(u'奖励金额',  default=0)
    def __unicode__(self):
        return self.user.username +',' + str(self.acc_num) + ','+str(self.award)+','+str(self.rank)
    class Meta:
        ordering = ['rank']

class GlobalStatis(models.Model):
    time = models.DateTimeField(u"统计时间", auto_now=True)
    all_wel_num = models.PositiveIntegerField(u"福利总数", default=0)
    award_total = models.PositiveIntegerField(u'累计奖励金额', default=0)

class Dict(models.Model):
    key = models.CharField(max_length=20,primary_key=True)
    value = models.CharField(max_length=512)
    expire_stamp = models.IntegerField()
    def __unicode__(self):
        return self.key + ':' + self.value