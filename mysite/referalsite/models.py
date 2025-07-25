import random
import string
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")


class User(models.Model):

    class Meta:
        indexes = [models.Index(fields=['phone_number'])]

    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    invite_code = models.CharField(max_length=6, unique=True, blank=True, null=True)
    activated_invite_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Номер телефона - {self.phone_number}"

    def generate_invite_code(self):
        while True:
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            if not User.objects.filter(invite_code=code).exists():
                return code

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self.generate_invite_code()
        super().save(*args, **kwargs)


class AuthCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Номер телефона и код - {self.user.phone_number} - {self.code}"