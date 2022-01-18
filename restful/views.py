from django.http import request
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from restful.models import Booking, Pool
from restful.permissions import IsBookingOwner
from .serializers import PoolSerializer, UserSerializer,\
                         MyTokenObtainPairSerializer,\
                         BookingSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from customuser.models import User

from django.utils import timezone


class RegisterAPIView(generics.CreateAPIView):
    """
    Expects an email, username and password to create user
    No authentication required
    No authorization required
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        """
        Validates email and password
        Returns:
            User details (email, username)
            Refresh and Access Token
            Status: 201
        Errors: 400
        """
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(id=response.data.get('id'))
        refresh = RefreshToken.for_user(user)

        return Response({
            'status': status.HTTP_201_CREATED,
            'message': 'User registered successfully',
            'user': response.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Used to provide user details, access and refresh token on 'login'
    """
    serializer_class = MyTokenObtainPairSerializer


class PoolViewSet(viewsets.ModelViewSet):
    """
    Only Admins can create, delete, or update a pool
    Any other person can list and retrieve a pool
    """
    queryset = Pool.objects.all().order_by('-created_at')
    serializer_class = PoolSerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['create', 'update',
                           'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user,
                        updated_at=timezone.now())


class BookingViewSet(viewsets.ModelViewSet):
    """
    Only admin can list all bookings
    Authenticated user can create a booking, update, destroy, retreive
    only their booking
    Authenticated user can view all their bookings
    """
    serializer_class = BookingSerializer
    queryset = Booking.objects.all().order_by('-created_at')
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAdminUser]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsBookingOwner]
        return [permission() for permission in permission_classes]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user,
                        updated_at=timezone.now())

    # TODO validate start and end datetime on create()
    # TODO fetch all Bookings by particular user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Only Admin can see all users
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
