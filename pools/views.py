from django.contrib.auth.models import AnonymousUser
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from pools.errors import BOOKING_INTEGRITY_ERROR,\
    RATING_INTEGRITY_ERROR, UNKOWN_USER_ERROR
from pools.helpers import create_token_for_new_user,\
    generate_recent_bookings_response,\
    generate_reset_password_confirm_response,\
    generate_reset_password_request_response,\
    generate_user_ratings_response

from pools.models import Booking, FileUpload, Pool, Rating, User
from pools.permissions import IsOwner
from pools.success_messages import USER_REGISTRATION_MESSAGE
from .serializers import FileUploadSerializer, PoolSerializer,\
                         RatingSerializer, ResetPasswordConfirmSerializer,\
                         ResetPasswordRequestSerializer, UserSerializer,\
                         MyTokenObtainPairSerializer,\
                         BookingSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Avg


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        token = create_token_for_new_user(response.data.get('id'))

        return Response({
            'status': status.HTTP_201_CREATED,
            'message': USER_REGISTRATION_MESSAGE,
            'user': response.data,
            'refresh': str(token),
            'access': str(token.access_token),
        }, status=status.HTTP_201_CREATED)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class PoolViewSet(viewsets.ModelViewSet):
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
        if isinstance(exc, IntegrityError):
            return Response(BOOKING_INTEGRITY_ERROR,
                            status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)

    @action(detail=False, permission_classes=[IsOwner])
    def recent_bookings(self, request):
        if type(request.user) == AnonymousUser:
            return Response(UNKOWN_USER_ERROR,
                            status=status.HTTP_401_UNAUTHORIZED)
        response = generate_recent_bookings_response(request, self)
        return response


class UserViewSet(viewsets.ReadOnlyModelViewSet):
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
        if type(request.user) == AnonymousUser:
            return Response(UNKOWN_USER_ERROR,
                            status=status.HTTP_401_UNAUTHORIZED)
        response = generate_user_ratings_response(request, self)
        return response

    def handle_exception(self, exc):
        if isinstance(exc, IntegrityError):
            return Response(RATING_INTEGRITY_ERROR,
                            status=status.HTTP_400_BAD_REQUEST)
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
    response = generate_reset_password_request_response(email)
    return response


@api_view(['POST'])
def reset_password_confirm_view(request, **kwargs):
    serializer = ResetPasswordConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    response = generate_reset_password_confirm_response(serializer, **kwargs)
    return response
