from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import PoolViewSet, RegisterAPIView, MyTokenObtainPairView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('pools', PoolViewSet, basename='pool')

urlpatterns = [
    path('users/login/', MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/register/', RegisterAPIView.as_view(), name='register_user'),
]

urlpatterns += router.urls
