from django.contrib.auth.models import AnonymousUser
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from restful.models import Booking, Pool
from restful.permissions import IsOwner
from .serializers import PoolSerializer, UserSerializer,\
                         MyTokenObtainPairSerializer,\
                         BookingSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from customuser.models import User

from django.utils import timezone
from django.db import IntegrityError


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
            permission_classes = [IsOwner]
        return [permission() for permission in permission_classes]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user,
                        updated_at=timezone.now())

    def handle_exception(self, exc):
        """
        Handle Integrity error when user tries to create
        same booking. Slug unique constraint will fail
        """
        if isinstance(exc, IntegrityError):
            error = 'You have already booked this pool.' + \
                    'Request an update if required'
            error = {"Integrity error": error}
            return Response(error, status.HTTP_400_BAD_REQUEST)
        else:
            return super().handle_exception(exc)

    @action(detail=False, permission_classes=[IsOwner])
    def recent_bookings(self, request):
        if type(request.user) == AnonymousUser:
            return Response({'detail': 'User not known'},
                            status=status.HTTP_401_UNAUTHORIZED)

        recent_bookings = Booking.objects.filter(user=request.user)\
            .order_by('-created_at')

        page = self.paginate_queryset(recent_bookings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(recent_bookings, many=True)
        return Response(serializer.data)


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
