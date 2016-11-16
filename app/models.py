from django.db import models
from account.models import MyUser

# Create your models here.
class UserToken(models.Model):
    token = models.CharField("token", max_length=32, primary_key=True)
    user = models.ForeignKey(MyUser,related_name = 'tokens',)
    expire = models.IntegerField(u"expire_time")