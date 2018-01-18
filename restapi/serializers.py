from wafuli.models import TransList, UserEvent
from rest_framework import serializers
from teaminvest.models import Project, Investlog, Backlog
from account.models import BankCard

# Create your views here.
class TransListSerializer(serializers.ModelSerializer):
    user_mobile = serializers.CharField(source='user.mobile', read_only=True)
    user_balance = serializers.CharField(source='balance', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = TransList
        fields = '__all__'

class TeamInvestLogSerializer(serializers.ModelSerializer):
    state_desc = serializers.CharField(source='get_audit_state_display', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    user_mobile = serializers.CharField(source='user.mobile', read_only=True)
    class Meta:
        model = Investlog
        fields = '__all__'
        read_only_fields = ('audit_state', 'settle_amount', 'submit_time', 'state_desc', 'user')

class BackLogSerializer(serializers.ModelSerializer):
    state_desc = serializers.CharField(source='get_audit_state_display', read_only=True)
    invest_date = serializers.DateField(source='investlog.invest_date', read_only=True)
    invest_amount = serializers.CharField(source='investlog.invest_amount', read_only=True)
    class Meta:
        model = Backlog
        fields = '__all__'
        
class BankcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankCard
        fields = '__all__'