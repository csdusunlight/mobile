#coding:utf-8
from django.shortcuts import render
from wafuli.models import TransList, UserEvent
from rest_framework import generics, permissions
from permissions import CsrfExemptSessionAuthentication
from restapi.permissions import IsOwnerOrStaff, IsAdmin
from restapi.serializers import TransListSerializer, TeamInvestLogSerializer,\
    TeamInvestLogSerializer, BackLogSerializer, BankcardSerializer
from restapi.Paginations import MyPageNumberPagination
import django_filters
from restapi.Filters import TranslistFilter, TeamInvestLogFilter, BackLogFilter
from teaminvest.models import Project, Investlog, Backlog
from account.models import BankCard
from rest_framework.exceptions import ValidationError

class BaseViewMixin(object):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    
class TranslistList(BaseViewMixin, generics.ListAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return TransList.objects.all()
        else:
            return TransList.objects.filter(user=user)
    permission_classes = (IsOwnerOrStaff,)
    serializer_class = TransListSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = TranslistFilter
    
class TeamProjectInvestLogList(BaseViewMixin, generics.ListCreateAPIView):
    serializer_class = TeamInvestLogSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = TeamInvestLogFilter
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Investlog.objects.all()
        else:
            return Investlog.objects.filter(user=user)
    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        if Investlog.objects.filter(user=self.request.user, project=project).exclude(audit_state='2').exists():
            raise ValidationError({'detail': u'同一个项目只能参与1次'})
        else:
            serializer.save(audit_state='1', user=self.request.user)
            

# class AdminTeamProjectInvestLogList(TeamProjectInvestLogList):
#     def get_queryset(self):
#         return Investlog.objects.all()
#     permission_classes = (IsAdmin,)
    
class TeamProjectInvestLogDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Investlog.objects.all()
    serializer_class = TeamInvestLogSerializer
    permission_classes = (IsOwnerOrStaff,)
    
class BackLogList(BaseViewMixin, generics.ListCreateAPIView):
    serializer_class = BackLogSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = BackLogFilter
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Backlog.objects.all()
        else:
            return Backlog.objects.filter(user=user)
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

# class AdminTeamProjectInvestLogList(TeamProjectInvestLogList):
#     def get_queryset(self):
#         return Investlog.objects.all()
#     permission_classes = (IsAdmin,)
    
class BackLogDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Investlog.objects.all()
    serializer_class = TeamInvestLogSerializer
    permission_classes = (IsAdmin,)
    
class BankcardList(BaseViewMixin, generics.ListAPIView):
    serializer_class = BankcardSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ['user']
    queryset = BankCard.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsAdmin)