from rest_framework import serializers
from rest_framework import status

from customuser.models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Booking, FileUpload, Pool, Rating
from django.utils import timezone


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
    average_rating = serializers.SerializerMethodField()

    def get_average_rating(self, obj):
        return obj.average_rating

    class Meta:
        model = Pool
        fields = ['url', 'id', 'name', 'location',
                  'day_price', 'thumbnail_url',
                  'image_url', 'width', 'length', 'depth_shallow_end',
                  'depth_deep_end', 'maximum_people', 'slug', 'created_at',
                  'average_rating'
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

    def validate_start_datetime(self, value):
        """
        Check if start_datetime is not past
        """
        if value < timezone.now():
            raise serializers.ValidationError('Start date can not be past')
        return value

    def validate_end_datetime(self, value):
        """
        Check if end_datetime is not past
        """
        if value < timezone.now():
            raise serializers.ValidationError('Start date can not be past')
        return value

    def validate(self, attrs):
        """
        Check if start_datetime is not > end_datetime
        """
        if attrs['start_datetime'] > attrs['end_datetime']:
            error = 'Start date must be less than or equal to end date'
            raise serializers.ValidationError(f'{error}')
        return attrs


class RatingSerializer(serializers.HyperlinkedModelSerializer):
    pool = serializers.HyperlinkedRelatedField(view_name='pool-detail',
                                               lookup_field='slug',
                                               queryset=Pool.objects.all())

    class Meta:
        model = Rating
        fields = ['url', 'user', 'pool', 'value', 'slug', 'created_at']
        lookup_field = 'slug'
        extra_kwargs = {
            'slug': {'read_only': True},
            'url': {'lookup_field': 'slug'},
            'user': {'read_only': True}
        }


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['id', 'file_name', 'file', 'uploaded_at']


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attr):
        if not User.objects.filter(email=attr['email']).exists():
            raise serializers.ValidationError('User for email not found')
        return attr


class ResetPasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField()
