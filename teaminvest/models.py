#coding:utf-8
from django.db import models
from django.utils import timezone
from account.models import MyUser
import datetime
# Create your models here.
Project_STATE = (
    ('00', u'即将开始'),
    ('10', u'正在进行'),
    ('20', u'已结束'),
    ('30', u'已删除'),
)
class Project(models.Model):
    title = models.CharField(u"项目标题", max_length=20)
    state = models.CharField(u"项目状态", max_length=2, choices=Project_STATE, default='10')
    create_date = models.DateField(u"创建日期", default=timezone.now)
    is_vip_bonus = models.BooleanField(u'适用VIP奖励', default=True)
    invest_account = models.CharField(u"平台账号", max_length=30, blank=True)
    invest_passwd = models.CharField(u"登录密码", max_length=30, blank=True)
    invest_amount = models.DecimalField(u'投资金额', max_digits=10, decimal_places=2, null=True, blank=True)
    back_amount = models.DecimalField(u'回款金额', max_digits=10, decimal_places=2, null=True, blank=True)
    def __unicode__(self):
        return self.title
    class Meta:
        verbose_name = u"组队投资项目"
        verbose_name_plural = u"组队投资项目"
        ordering = ["-create_date"]

def get_today():
    return datetime.date.today()
AUDIT_STATE = (
    ('0', u'审核通过'),
    ('1', u'待审核'),
    ('2', u'审核未通过'),
    ('3', u'复审'),
)
class Investlog(models.Model):
    user = models.ForeignKey(MyUser, related_name="investlog_submit")
    project = models.ForeignKey(Project, related_name="investlogs")
    submit_time = models.DateTimeField(u'提交时间', default=timezone.now)
    invest_amount = models.DecimalField(u'投资金额', max_digits=10, decimal_places=2)
    invest_date = models.DateField(u'投资日期', default=get_today)
    remark = models.CharField(u"备注", max_length=100, blank=True)
    settle_amount = models.DecimalField(u'结算金额', max_digits=10, decimal_places=2, null=True)
    audit_time = models.DateTimeField(u'审核时间', default=timezone.now)
    audit_state = models.CharField(max_length=10, choices=AUDIT_STATE, verbose_name=u"审核状态")
    audit_reason = models.CharField(max_length=100, verbose_name=u"审核说明", blank=True)
    def __unicode__(self):
        return u"用户：%s 投资项目：%s 投资金额：%s" % (self.user, self.project.title, self.invest_amount)
    class Meta:
        ordering = ["-submit_time",]
        unique_together = (('user', 'project'),)
    def get_encrypt_mobile(self):
        mobile = self.mobile
        if len(mobile)>=7:
            return mobile[:3] + '****' + mobile[-4:]
        else:
            return mobile

class Backlog(models.Model):
    user = models.ForeignKey(MyUser, related_name="backlog")
    project = models.ForeignKey(Project, related_name="backlogs")
    investlog = models.ForeignKey(Investlog, related_name="backlogs")
    back_amount = models.DecimalField(u'回款金额', max_digits=10, decimal_places=2)
    back_date = models.DateField(u'回款日期', default=get_today)
    remark = models.CharField(u"备注", max_length=100, blank=True)
    def __unicode__(self):
        return u"用户：%s 项目：%s 回款金额：%s" % (self.user, self.project.title, self.back_amount)
    class Meta:
        ordering = ["-back_date",]
