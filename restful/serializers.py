from rest_framework import serializers
from rest_framework import status

from customuser.models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Booking, Pool


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


class PoolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pool
        fields = ['url', 'id', 'name', 'location',
                  'day_price', 'thumbnail_url',
                  'image_url', 'width', 'length', 'depth_shallow_end',
                  'depth_deep_end', 'maximum_people', 'slug', 'created_at'
                  ]
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'},
            'slug': {'read_only': True},
        }


class BookingSerializer(serializers.HyperlinkedModelSerializer):
    pool_name = serializers.ReadOnlyField(source='pool.name')
    pool = serializers.HyperlinkedRelatedField(view_name="pool-detail",
                                               lookup_field='slug',
                                               queryset=Pool.objects.all())
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Booking
        fields = ['id', 'url', 'total_amount', 'start_datetime',
                  'end_datetime', 'slug', 'created_at',
                  'pool_name', 'pool', 'user_name', 'user'
                  ]
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'},
            'slug': {'read_only': True},
            'total_amount': {'read_only': True}
        }
