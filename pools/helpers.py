from pools.errors import (
    INVALID_REQUEST_ERROR,
    INVALID_RESET_LINK,
    REQUEST_PASSWORD_RESET_ERROR,
    UNKOWN_USER_ERROR,
)
from pools.models import User, Booking, Rating
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.utils.http import urlsafe_base64_decode

from pools.success_messages import (
    PASSWORD_CHANGED_SUCCESS,
    REQUEST_PASSWORD_RESET_MESSAGE,
    REQUEST_PASSWORD_RESET_SUBJECT,
)


def create_token_for_new_user(id):
    user = User.objects.get(id=id)
    # Set password because password not being hashed after adding DRF
    user.set_password(user.password)
    user.save()
    token = RefreshToken.for_user(user)
    return token


def modify_token_obtain_pair_serializer_data(data, self_object):
    refresh = self_object.get_token(self_object.user)
    data["status"] = status.HTTP_200_OK
    data["message"] = "Request successfull"
    data["refresh"] = str(refresh)
    data["access"] = str(refresh.access_token)
    data["user"] = {
        "username": self_object.user.username,
        "email": self_object.user.email,
        "id": self_object.user.id,
    }
    return data


def generate_recent_bookings_response(request, self_object):
    recent_bookings = Booking.objects.filter(user=request.user).order_by("-created_at")

    page = self_object.paginate_queryset(recent_bookings)

    if page is not None:
        serializer = self_object.get_serializer(page, many=True)
        return self_object.get_paginated_response(serializer.data)

    serializer = self_object.get_serializer(recent_bookings, many=True)

    return Response(serializer.data)


def generate_user_ratings_response(request, self_object):
    user_ratings = Rating.objects.filter(user=request.user).order_by("-created_at")

    page = self_object.paginate_queryset(user_ratings)
    if page is not None:
        serializer = self_object.get_serializer(page, many=True)
        return self_object.get_paginated_response(serializer.data)

    serializer = self_object.get_serializer(user_ratings, many=True)
    return Response(serializer.data)


def generate_reset_password_request_response(email):
    user = User.objects.get(email=email)

    uidb64 = urlsafe_base64_encode(force_bytes(user.id))

    token = PasswordResetTokenGenerator().make_token(user)

    reset_link = f"{settings.FRONTEND_URL}/{uidb64}/{token}/"
    print(reset_link)
    body = (
        "Please use the link below to reset your password \n"
        + f"{reset_link} \n"
        + "If you did not request this, please ignore this email"
    )

    try:
        send_mail(REQUEST_PASSWORD_RESET_SUBJECT, body, settings.FROM_EMAIL, [email])
    except Exception as e:
        print(f"{REQUEST_PASSWORD_RESET_ERROR}: {e}")
        return Response(
            REQUEST_PASSWORD_RESET_ERROR, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(REQUEST_PASSWORD_RESET_MESSAGE, status=status.HTTP_200_OK)


def generate_reset_password_confirm_response(serializer, **kwargs):
    uidb64 = kwargs.get("uidb64")
    token = kwargs.get("token")

    if not uidb64 or not token:
        return Response(INVALID_REQUEST_ERROR, status=status.HTTP_400_BAD_REQUEST)

    uid = urlsafe_base64_decode(uidb64)

    user = User.objects.filter(pk=uid)
    if not user or not user[0]:
        return Response(UNKOWN_USER_ERROR, status=status.HTTP_401_UNAUTHORIZED)

    is_token_valid = PasswordResetTokenGenerator().check_token(user[0], token)

    if not is_token_valid:
        return Response(INVALID_RESET_LINK, status=status.HTTP_401_UNAUTHORIZED)

    new_password = serializer.data.get("new_password")
    user[0].set_password(new_password)
    user[0].save()

    return Response(PASSWORD_CHANGED_SUCCESS, status=status.HTTP_200_OK)
