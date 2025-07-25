from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, AuthCode
from .serializers import UserSerializer, AuthCodeSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields = ['activated_invite_code', 'created_at']
    search_fields = ['phone_number', 'invite_code']
    ordering_fields = ['created_at', 'phone_number']


class AuthCodeViewSet(ModelViewSet):
    queryset = AuthCode.objects.all()
    serializer_class = AuthCodeSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_fields = ['user', 'is_used', 'created_at']
    ordering_fields = ['created_at', 'user']