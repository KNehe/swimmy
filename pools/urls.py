from django.urls import path, re_path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import FileUploadView, RatingViewSet, UserViewSet, BookingViewSet,\
                   PoolViewSet, RegisterAPIView, MyTokenObtainPairView,\
                   reset_password_confirm_view, reset_password_request_view
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings

router = DefaultRouter()
router.register('pools', PoolViewSet, basename='pool')
router.register('bookings', BookingViewSet, basename='booking')
router.register('view-users', UserViewSet, basename='user')
router.register('ratings', RatingViewSet, basename='rating')
router.register('uploads', FileUploadView, basename='upload')

schema_view = get_schema_view(
     openapi.Info(
          title='Swimmy API',
          default_version='v1',
          description="REST API that powers swimmy apps",
          contact=openapi.Contact(email=settings.FROM_EMAIL),
          license=openapi.License(name='BSD License')
     ),
     public=True,
     permission_classes=[AllowAny]
)

urlpatterns = [
    path('users/login/', MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('tokens/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/register/', RegisterAPIView.as_view(), name='register_user'),
    path('users/reset_password/', reset_password_request_view,
         name='reset_password_request'),
    path('users/reset_password_confirm/<uidb64>/<token>/',
         reset_password_confirm_view,
         name='reset_password_confirm_view'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    re_path(r'^swagger/$',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
    re_path(r'^redoc/$',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
]

urlpatterns += router.urls
