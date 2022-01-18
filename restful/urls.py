from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import UserViewSet, BookingViewSet, PoolViewSet, RegisterAPIView, MyTokenObtainPairView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('pools', PoolViewSet, basename='pool')
router.register('bookings', BookingViewSet, basename='booking')
router.register('view-users', UserViewSet, basename='user')

urlpatterns = [
    path('users/login/', MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('tokens/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/register/', RegisterAPIView.as_view(), name='register_user'),
]

urlpatterns += router.urls
