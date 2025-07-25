import random
import time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.views import View
from django.views.generic import TemplateView
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny

from .models import User, AuthCode
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .serializers import (
    UserSerializer, AuthCodeSerializer
)


phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Номер телефона должен быть вот в "
                                                               "таком формате: '+375(29)1112233'")


def generate_auth_code():
    """Генерирует 4-значный код авторизации"""
    return f"{random.randint(1000, 9999)}"


# --- ViewSets для CRUD операций ---
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activated_invite_code', 'created_at']
    search_fields = ['phone_number', 'invite_code']
    ordering_fields = ['created_at', 'phone_number']

class AuthCodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления кодами авторизации.
    """
    queryset = AuthCode.objects.all()
    serializer_class = AuthCodeSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user', 'is_used', 'created_at']
    ordering_fields = ['created_at', 'user']




class PhoneRequiredMixin:
    """Миксин для проверки, есть ли номер телефона в сессии"""
    def dispatch(self, request, *args, **kwargs):
        if 'phone_number' not in request.session:
            messages.error(request, "Вы должны войти в систему")
            return redirect('send_code')
        return super().dispatch(request, *args, **kwargs)


class SendCodeView(View):
    """ Страница ввода номера телефона и отправки кода"""

    def get(self, request):
        if 'phone_number' in request.session:
            return redirect('profile')
        return render(request, 'referalsite/send_code.html')

    def post(self, request):
        phone_number = request.POST.get('phone_number').strip()
        if not phone_number:
            messages.error(request, "Пожалуйста введите номер телефона.")
            return render(request, 'referalsite/send_code.html')

        try:
            # Проверка на существующий номер телефона и корректность номера телефона
            user, created = User.objects.get_or_create(phone_number=phone_number)
        except ValidationError as e:
            messages.error(request, f"Ошибка при обработке номера: {', '.join(e.messages)}")
            return render(request, 'referalsite/send_code.html')
        except Exception as e:
            messages.error(request, f"Произошла ошибка: {str(e)}")
            return render(request, 'referalsite/send_code.html')

        try:
            phone_regex(phone_number)
        except Exception as e:
            messages.error(request, f"Некорректный номер телефона: {e.message}")
            return render(request, 'referalsite/send_code.html')

        time.sleep(random.uniform(1, 2))

        code = generate_auth_code()

        AuthCode.objects.create(user=user, code=code)

        request.session['temp_phone'] = phone_number
        request.session['temp_code'] = code

        messages.info(request, f"Код отправлен на номер {phone_number}.({code})")
        return redirect('verify_code')


class VerifyCodeView(View):
    """Страница ввода и проверки кода авторизации"""

    def get(self, request):
        # Проверяем, есть ли временные данные
        temp_phone = request.session.get('temp_phone')
        if not temp_phone:
            messages.error(request, "Введите ваш номер телефона.")
            return redirect('send_code')
        return render(request, 'referalsite/verify_code.html', {'phone_number': temp_phone})

    def post(self, request):
        temp_phone = request.session.get('temp_phone')
        temp_code = request.session.get('temp_code')
        entered_code = request.POST.get('code')

        if not temp_phone or not temp_code:
            messages.error(request, "Ваша сессия окончена, войдите заново")
            return redirect('send_code')

        if entered_code == temp_code:
            try:
                user = User.objects.get(phone_number=temp_phone)

                del request.session['temp_phone']
                del request.session['temp_code']

                request.session['phone_number'] = user.phone_number

                messages.success(request, "Успешный вход!")
                return redirect('profile')
            except User.DoesNotExist:
                messages.error(request, "Нет такого номера телефона, попробуйте заново")
                return redirect('send_code')
        else:
            messages.error(request, "Неверный код. Попробуйте заново.")
            return render(request, 'referalsite/verify_code.html', {'phone_number': temp_phone})


class ProfileView(PhoneRequiredMixin, TemplateView):
    """Страница профиля пользователя"""
    template_name = 'referalsite/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        phone_number = self.request.session.get('phone_number')
        if phone_number:
            try:
                user = User.objects.get(phone_number=phone_number)
                invited_users = User.objects.filter(activated_invite_code=user.invite_code)

                context['user'] = user
                context['invited_users'] = invited_users
            except User.DoesNotExist:
                messages.error(self.request, "Нет такого пользователя.")
                logout(self.request)
        else:
            messages.error(self.request, "Вы не вошли в аккаунт.")
        return context


class ActivateInviteView(PhoneRequiredMixin, View):
    """активация инвайт-кода"""

    def post(self, request):
        phone_number = request.session.get('phone_number')
        invite_code_to_activate = request.POST.get('invite_code')

        if not phone_number or not invite_code_to_activate:
            messages.error(request, "Не верные значения.")
            return redirect('profile')

        try:
            user = User.objects.get(phone_number=phone_number)

            if user.activated_invite_code:
                messages.error(request, "Вы уже ввели код приглашения.")
                return redirect('profile')

            if user.invite_code == invite_code_to_activate:
                messages.error(request, "Вы не можете активировать свой код приглашения.")
                return redirect('profile')

            if not User.objects.filter(invite_code=invite_code_to_activate).exists():
                messages.error(request, "Не верный код приглашения.")
                return redirect('profile')

            user.activated_invite_code = invite_code_to_activate
            user.save()

            messages.success(request, "Успешная активация кода приглашения!")

        except User.DoesNotExist:
            messages.error(request, "Пользователь не найден.")
        except Exception as e:
            messages.error(request, f"Ошибка: {e}")

        return redirect('profile')


class LogoutView(View):
    """Выход из системы"""

    def post(self, request):
        request.session.flush()
        messages.info(request, "Вы вышли из аккаунта.")
        return redirect('send_code')

