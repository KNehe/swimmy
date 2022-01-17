from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from customuser.models import User


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
    serializer_class = MyTokenObtainPairSerializer
