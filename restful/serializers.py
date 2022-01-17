from rest_framework import serializers
from rest_framework import status

from customuser.models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}, }

    def create(self, validated_data):
        return User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            password=make_password(validated_data['password'])
        )


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['status'] = status.HTTP_200_OK
        data['message'] = 'Request successfull'
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = {'username': self.user.username,
                        'email': self.user.email,
                        'id': self.user.id,
                        }
        return data
