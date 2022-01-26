from email import message
import email
from django.contrib.auth.models import AnonymousUser
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from sqlparse import tokens
from django.core.mail import send_mail

from restful.models import Booking, FileUpload, Pool, Rating
from restful.permissions import IsOwner
from .serializers import FileUploadSerializer, PoolSerializer,\
                         RatingSerializer, ResetPasswordConfirmSerializer,\
                         ResetPasswordRequestSerializer, UserSerializer,\
                         MyTokenObtainPairSerializer,\
                         BookingSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from customuser.models import User

from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Avg
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes


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
    serializer_class = PoolSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Pool.objects.all().\
               annotate(_average_value=Avg('rating__value')).\
               order_by('-created_at')

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


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    queryset = Rating.objects.all().order_by('-created_at')
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        if self.action == 'list':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsOwner]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, permission_classes=[IsOwner])
    def user_ratings(self, request):
        """
        Get all ratings made by a user
        """
        if not request.user or type(request.user) == AnonymousUser:
            return Response({'detail': 'User not known'},
                            status=status.HTTP_401_UNAUTHORIZED)

        user_ratings = Rating.objects.filter(user=request.user)\
                                     .order_by('-created_at')

        page = self.paginate_queryset(user_ratings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(serializer.data)

        serializer = self.get_serializer(user_ratings, many=True)
        return Response(serializer.data)

    def handle_exception(self, exc):
        """
        Handle exception when user attempts to recreate
        a rating
        Should request update from existing rating
        """
        if isinstance(exc, IntegrityError):
            error = 'Already rated! request update to make changes'
            error = {'Integrity Error': error}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super().handle_exception(exc)


class FileUploadView(viewsets.ModelViewSet):
    queryset = FileUpload.objects.all().order_by('-uploaded_at')
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = FileUploadSerializer


@api_view(['POST'])
def reset_password_request_view(request):
    serializer = ResetPasswordRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.data.get('email')

    user = User.objects.get(email=email)

    uidb64 = urlsafe_base64_encode(force_bytes(user.id))

    token = PasswordResetTokenGenerator().make_token(user)

    reset_link = f'{settings.FRONTEND_URL}/{uidb64}/{token}/'

    body = 'Please use the link below to reset your password \n' + \
           f'{reset_link} \n' + \
           'If you did not request this, please ignore this email'

    try:
        send_mail('Swimmy App Reset Password',
                  body, settings.FROM_EMAIL, [email])
    except Exception as e:
        print(f'SEND RESET PASSWORD EMAIL ERROR: {e}')
        message = {"message": "An error occurred, try again later"}
        return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    message = {"message": "We sent a reset password link to your email"}

    return Response(message, status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password_confirm_view(request, **kwargs):
    serializer = ResetPasswordConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    uidb64 = kwargs.get('uidb64')
    token = kwargs.get('token')

    if not uidb64 or not token:
        message = {'message': 'Invalid request'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    uid = urlsafe_base64_decode(uidb64)

    user = User.objects.filter(pk=uid)
    if not user or not user[0]:
        message = {'message': 'Request for unknown user'}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    is_token_valid = PasswordResetTokenGenerator().check_token(user[0], token)

    if not is_token_valid:
        message = {'message': 'Reset link is now invalid'}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    new_password = serializer.data.get('new_password')
    user[0].set_password(new_password)
    user[0].save()

    message = {'message': 'Password successfully changed'}
    return Response(message, status=status.HTTP_200_OK)
