from wafuli.models import TransList, UserEvent
from rest_framework import serializers
from teaminvest.models import Project, Investlog, Backlog

# Create your views here.
class TransListSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(source='user.mobile', read_only=True)
    user_balance = serializers.CharField(source='balance', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = TransList
        fields = '__all__'

class TeamInvestLogSerializer(serializers.ModelSerializer):
    state_desc = serializers.CharField(source='get_audit_state_display', read_only=True)
    class Meta:
        model = Investlog
        fields = '__all__'
        read_only_fields = ('audit_state', 'settle_amount', 'submit_time', 'state_desc', 'user')

class BackLogSerializer(serializers.ModelSerializer):
    state_desc = serializers.CharField(source='get_audit_state_display', read_only=True)
    class Meta:
        model = Backlog
        fields = '__all__'