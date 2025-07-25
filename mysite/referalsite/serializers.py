from rest_framework import serializers
from .models import User, AuthCode


class SendCodeSerializer(serializers.Serializer):
    """Сериализатор для отправки кода авторизации"""
    phone_number = serializers.CharField(max_length=17)

    def validate_phone_number(self, value):
        from django.core.validators import RegexValidator
        phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Номер телефона должен быть в формате: '+999999999'. Допускается до 15 цифр.")
        phone_regex(value)
        return value.strip()


class VerifyCodeSerializer(serializers.Serializer):
    """Сериализатор для проверки кода авторизации"""
    phone_number = serializers.CharField(max_length=17)
    code = serializers.CharField(max_length=4, min_length=4)


class ActivateInviteSerializer(serializers.Serializer):
    """Сериализатор для активации инвайт-кода"""
    invite_code = serializers.CharField(max_length=6, min_length=6)

    def validate_invite_code(self, value):
        if not User.objects.filter(invite_code=value).exists():
            raise serializers.ValidationError("Неверный код приглашения.")
        return value


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User"""
    invited_users = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'invite_code', 'activated_invite_code', 'created_at', 'invited_users']
        read_only_fields = ['id', 'invite_code', 'created_at', 'invited_users']

    def get_invited_users(self, obj):
        invited = User.objects.filter(activated_invite_code=obj.invite_code)
        return [user.phone_number for user in invited]

    def validate_phone_number(self, value):
        from django.core.validators import RegexValidator
        phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Номер телефона должен быть в формате: '+999999999'. Допускается до 15 цифр.")
        phone_regex(value)
        return value.strip()

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.activated_invite_code = validated_data.get('activated_invite_code', instance.activated_invite_code)
        instance.save()
        return instance


class AuthCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthCode
        fields = ('id', 'user', 'code', 'created_at', 'is_used')
        read_only_fields = ('id', 'user', 'code', 'created_at', 'is_used')


class UserProfileSerializer(serializers.ModelSerializer):
    invited_users = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('phone_number', 'invite_code', 'activated_invite_code', 'invited_users')
        read_only_fields = ('phone_number', 'invite_code', 'activated_invite_code', 'invited_users')

    def get_invited_users(self, obj):
        invited = User.objects.filter(activated_invite_code=obj.invite_code)
        return [user.phone_number for user in invited]


class AuthSuccessResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user_id = serializers.IntegerField()


class AuthErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()


class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()