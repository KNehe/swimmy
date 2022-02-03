from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from pools.errors import END_DATE_PAST_ERROR, START_DATE_ERROR,\
    START_DATE_PAST_ERROR, USER_FOR_EMAIL_NOT_FOUND_ERROR

from pools.helpers import modify_token_obtain_pair_serializer_data
from .models import Booking, FileUpload, Pool, Rating, User
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}, }


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data = modify_token_obtain_pair_serializer_data(data, self)

        return data


class PoolSerializer(serializers.HyperlinkedModelSerializer):
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
            raise serializers.ValidationError(START_DATE_PAST_ERROR)
        return value

    def validate_end_datetime(self, value):
        """
        Check if end_datetime is not past
        """
        if value < timezone.now():
            raise serializers.ValidationError(END_DATE_PAST_ERROR)
        return value

    def validate(self, attrs):
        """
        Check if start_datetime is not > end_datetime
        """
        if attrs['start_datetime'] > attrs['end_datetime']:
            raise serializers.ValidationError(START_DATE_ERROR)
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
            raise serializers.ValidationError(USER_FOR_EMAIL_NOT_FOUND_ERROR)
        return attr


class ResetPasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField()
