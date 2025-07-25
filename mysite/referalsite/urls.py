
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from .views import UserViewSet, AuthCodeViewSet, SendCodeView, VerifyCodeView, ProfileView, ActivateInviteView, LogoutView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'auth-codes', AuthCodeViewSet)

urlpatterns = [
    path('', SendCodeView.as_view(), name='send_code'),
    path('verify/', VerifyCodeView.as_view(), name='verify_code'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/activate-invite/', ActivateInviteView.as_view(), name='activate_invite'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('api/', include(router.urls)),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]