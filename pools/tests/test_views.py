from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status

import json
from datetime import timedelta

from pools.success_messages import USER_REGISTRATION_MESSAGE
from .helpers import create_test_pool, create_test_user
from pools.errors import END_DATE_PAST_ERROR, START_DATE_ERROR, START_DATE_PAST_ERROR
from pools.models import User


class RegisterAPIViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = {
            "username": "nehe",
            "email": "neeh@gmail.com",
            "password": "#$23msnAB",
        }

    def test_should_register_user(self):
        response = self.client.post(reverse("register_user"), self.user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("message"), USER_REGISTRATION_MESSAGE)
        self.assertEqual(response.data.get("user").get("email"), self.user["email"])
        self.assertIsNotNone(response.data.get("refresh"))
        self.assertIsNotNone(response.data.get("access"))
        self.assertEqual(User.objects.all().count(), 1)

    def test_should_not_register_user_with_invalid_email(self):
        self.user["email"] = "invalid@email"

        response = self.client.post(reverse("register_user"), self.user)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("email")[0].title(),
            "Enter A Valid Email Address.",
        )
        self.assertEqual(response.data.get("email")[0].code, "invalid")
        self.assertEqual(User.objects.all().count(), 0)

    def test_should_not_register_user_twice(self):
        response = self.client.post(reverse("register_user"), self.user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response2 = self.client.post(reverse("register_user"), self.user)

        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response2.data.get("username")[0].lower(),
            "a user with that username already exists.",
        )
        self.assertEqual(response2.data.get("username")[0].code, "unique")
        self.assertEqual(
            response2.data.get("email")[0].lower(),
            "user with this email already exists.",
        )
        self.assertEqual(response2.data.get("email")[0].code, "unique")
        self.assertEqual(User.objects.all().count(), 1)

    def test_should_not_register_without_all_data(self):
        """Should not register a user when email, password, and email are not given"""
        self.user["email"] = ""
        self.user["username"] = ""
        self.user["password"] = ""

        response = self.client.post(reverse("register_user"), self.user)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("email")[0].lower(), "this field may not be blank."
        )
        self.assertEqual(response.data.get("email")[0].code, "blank")
        self.assertEqual(
            response.data.get("password")[0].lower(), "this field may not be blank."
        )
        self.assertEqual(response.data.get("password")[0].code, "blank")
        self.assertEqual(
            response.data.get("username")[0].lower(), "this field may not be blank."
        )
        self.assertEqual(response.data.get("username")[0].code, "blank")
        self.assertEqual(User.objects.all().count(), 0)

    def test_should_not_register_user_when_only_email_missing(self):
        self.user["email"] = ""

        response = self.client.post(reverse("register_user"), self.user)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data.get("email")[0].lower(), "this field may not be blank."
        )
        self.assertEqual(response.data.get("email")[0].code, "blank")

    def test_should_not_register_user_when_only_username_missing(self):
        self.user["username"] = ""

        response = self.client.post(reverse("register_user"), self.user)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("username")[0].lower(), "this field may not be blank."
        )
        self.assertEqual(response.data.get("username")[0].code, "blank")

    def test_should_not_register_user_when_only_passowrd_missing(self):
        self.user["password"] = ""

        response = self.client.post(reverse("register_user"), self.user)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("password")[0].lower(), "this field may not be blank."
        )
        self.assertEqual(response.data.get("password")[0].code, "blank")


class MyTokenObtainPairViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = {
            "username": "8Nehe",
            "email": "neeh@gmail.com",
            "password": "#$23msnAB",
        }

    def test_should_retrieve_access_tokens(self):
        # create the user
        response = self.client.post(reverse("register_user"), self.user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # login / get tokens when not a registeration
        response2 = self.client.post(reverse("token_obtain_pair"), self.user)

        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response2.data.get("access"))
        self.assertIsNotNone(response2.data.get("refresh"))

    def test_should_not_get_access_tokens_when_user_not_registered(self):
        response = self.client.post(reverse("token_obtain_pair"), self.user)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data.get("detail").lower(),
            "no active account found with the given credentials",
        )
        self.assertEqual(response.data.get("detail").code, "no_active_account")

    def test_should_not_get_access_tokens_when_email_empty(self):
        self.client.post(reverse("register_user"), self.user)

        self.user["email"] = ""

        response = self.client.post(reverse("token_obtain_pair"), self.user)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("email")[0].lower(),
            "this field may not be blank.",
        )
        self.assertEqual(response.data.get("email")[0].code, "blank")

    def test_should_not_get_access_tokens_when_password_empty(self):
        self.client.post(reverse("register_user"), self.user)

        self.user["password"] = ""

        response = self.client.post(reverse("token_obtain_pair"), self.user)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("password")[0].lower(),
            "this field may not be blank.",
        )
        self.assertEqual(response.data.get("password")[0].code, "blank")

    def test_should_not_get_access_tokens_when_password_and_email_are_empty(self):
        self.client.post(reverse("register_user"), self.user)

        self.user["password"] = ""
        self.user["email"] = ""

        response = self.client.post(reverse("token_obtain_pair"), self.user)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("password")[0].lower(),
            "this field may not be blank.",
        )
        self.assertEqual(response.data.get("password")[0].code, "blank")
        self.assertEqual(
            response.data.get("email")[0].lower(),
            "this field may not be blank.",
        )
        self.assertEqual(response.data.get("email")[0].code, "blank")


class PoolsTest(APITestCase):
    def setUp(self):
        self.pool = {
            "name": "Nehe Ducks",
            "location": "Nboa road Mbale uganda",
            "day_price": "10.0",
            "thumbnail_url": "https://aws.s3.com/images/pic.png/",
            "image_url": "https://aws.s3.com/images/pic.png/",
            "width": "4.0",
            "length": "8.2",
            "depth_shallow_end": "1.0",
            "depth_deep_end": "3.0",
            "maximum_people": 15,
        }
        self.user = {
            "username": "8Nehe",
            "email": "nehe@gmail.com",
            "password": "#$23msnAB",
        }
        self.admin = User.objects.create_superuser(
            "myuser", "myemail@test.com", "$#@12D"
        )

    def authenticate(self):
        self.client.post(reverse("register_user"), self.user)

        response = self.client.post(reverse("token_obtain_pair"), self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data.get('access')}"
        )

    def authenticate_admin(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "myuser", "email": "myemail@test.com", "password": "$#@12D"},
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data.get('access')}"
        )

    def test_should_not_create_pool_when_user_not_admin(self):
        self.authenticate()
        response = self.client.post(reverse("pool-list"), self.pool)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get("detail").lower(),
            "you do not have permission to perform this action.",
        )
        self.assertEqual(response.data.get("detail").code, "permission_denied")

    def test_should_create_pool_when_user_is_admin(self):
        self.authenticate_admin()
        response = self.client.post(reverse("pool-list"), self.pool)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data.get("slug"), "nehe-ducks"
        )  # Nehe Ducks -> nehe-ducks
        self.assertEqual(response.data.get("name"), self.pool["name"])
        self.assertEqual(response.data.get("location"), self.pool["location"])
        self.assertEqual(response.data.get("day_price"), self.pool["day_price"])
        self.assertEqual(response.data.get("thumbnail_url"), self.pool["thumbnail_url"])
        self.assertEqual(response.data.get("image_url"), self.pool["image_url"])
        self.assertEqual(response.data.get("width"), self.pool["width"])
        self.assertEqual(response.data.get("length"), self.pool["length"])
        self.assertIsNone(response.data.get("average_rating"))
        self.assertEqual(
            response.data.get("maximum_people"), self.pool["maximum_people"]
        )
        self.assertEqual(
            response.data.get("depth_shallow_end"), self.pool["depth_shallow_end"]
        )
        self.assertEqual(
            response.data.get("depth_deep_end"), self.pool["depth_deep_end"]
        )

    def test_should_not_create_same_pool_twice(self):
        self.authenticate_admin()

        self.client.post(reverse("pool-list"), self.pool)
        response = self.client.post(reverse("pool-list"), self.pool)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("name")[0].lower(), "pool with this name already exists."
        )
        self.assertEqual(response.data.get("name")[0].code, "unique")

    def test_should_paginated_response_of_pools(self):
        create_test_pool(self.admin)
        url = reverse("pool-list")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        from_json = json.loads(response.content)
        to_json = json.dumps(from_json)

        self.assertIn("count", to_json)
        self.assertIn("next", to_json)
        self.assertIn("previous", to_json)
        self.assertIn("results", to_json)
        self.assertEqual(from_json.get("count"), 1)

    def test_should_not_create_same_pool_with_invalid_data(self):
        self.authenticate_admin()

        self.pool["day_price"] = "1000"
        self.pool["width"] = "10.999"
        self.pool["length"] = "101.999"
        self.pool["depth_shallow_end"] = "10.999"
        self.pool["depth_deep_end"] = "10.999"

        response = self.client.post(reverse("pool-list"), self.pool)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("day_price")[0].lower(),
            "ensure that there are no more than 3 digits in total.",
        )
        self.assertEqual(
            response.data.get("width")[0].lower(),
            "ensure that there are no more than 3 digits in total.",
        )
        self.assertEqual(
            response.data.get("length")[0].lower(),
            "ensure that there are no more than 3 digits in total.",
        )
        self.assertEqual(
            response.data.get("depth_shallow_end")[0].lower(),
            "ensure that there are no more than 2 digits in total.",
        )
        self.assertEqual(
            response.data.get("depth_deep_end")[0].lower(),
            "ensure that there are no more than 2 digits in total.",
        )

    def test_should_not_create_same_pool_with_empty_data(self):
        self.authenticate_admin()

        self.pool["day_price"] = ""
        self.pool["width"] = ""
        self.pool["length"] = ""
        self.pool["depth_shallow_end"] = ""
        self.pool["depth_deep_end"] = ""
        self.pool["name"] = ""

        response = self.client.post(reverse("pool-list"), self.pool)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("name")[0].lower(),
            "this field may not be blank.",
        )
        self.assertEqual(
            response.data.get("day_price")[0].lower(),
            "a valid number is required.",
        )
        self.assertEqual(
            response.data.get("width")[0].lower(),
            "a valid number is required.",
        )
        self.assertEqual(
            response.data.get("length")[0].lower(),
            "a valid number is required.",
        )
        self.assertEqual(
            response.data.get("depth_shallow_end")[0].lower(),
            "a valid number is required.",
        )
        self.assertEqual(
            response.data.get("depth_deep_end")[0].lower(),
            "a valid number is required.",
        )

    def test_should_update_pool(self):
        self.authenticate_admin()
        response = self.client.post(reverse("pool-list"), self.pool)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data.get("slug"), "nehe-ducks"
        )  # Nehe Ducks -> nehe-ducks
        self.assertEqual(response.data.get("name"), self.pool["name"])
        self.assertEqual(response.data.get("location"), self.pool["location"])

        # Update
        self.pool["name"] = "updated name"
        self.pool["location"] = "updated location"
        response2 = self.client.patch(
            reverse("pool-detail", kwargs={"slug": response.data.get("slug")}),
            self.pool,
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data.get("name"), self.pool["name"])
        self.assertNotEqual(response2.data.get("name"), response.data.get("name"))
        self.assertEqual(response2.data.get("location"), self.pool["location"])
        self.assertNotEqual(
            response2.data.get("location"), response.data.get("location")
        )
        self.assertEqual(response2.data.get("length"), response.data.get("length"))
        self.assertEqual(
            response2.data.get("image_url"), response.data.get("image_url")
        )


class BookingTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            "myuser", "myemail@test.com", "$#@12D"
        )
        self.pool = create_test_pool(user=self.admin)
        self.db_user = create_test_user(email="nehe2@gmail.com")
        self.user = {
            "username": "8Nehe",
            "email": "nehe@gmail.com",
            "password": "#$23msnAB",
        }
        self.password = "123Deaally"
        self.email = "nehe2@gmail.com"
        self.pool_url = f"http://testserver/api/v1/pools/{self.pool.slug}/"
        self.user_url = f"http://testserver/api/v1/view-users/{self.db_user.id}/"
        self.start = timezone.now() + timedelta(days=1)
        self.end = timezone.now() + timedelta(days=3)
        self.payload = {
            "pool": self.pool_url,
            "user": self.user_url,
            "start_datetime": self.start,
            "end_datetime": self.end,
        }

    def authenticate(self):
        self.client.post(reverse("register_user"), self.user)

        response = self.client.post(reverse("token_obtain_pair"), self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data.get('access')}"
        )

    def authenticate_admin(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "myuser", "email": "myemail@test.com", "password": "$#@12D"},
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data.get('access')}"
        )

    def test_should_book_a_pool(self):
        self.authenticate()
        response = self.client.post(reverse("booking-list"), self.payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data.get("pool_name"), self.pool.name)
        self.assertEqual(
            response.data.get("start_datetime"),
            self.start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        self.assertEqual(
            response.data.get("end_datetime"),
            self.end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        self.assertEqual(response.data.get("pool"), self.pool_url)
        self.assertEqual(response.data.get("user"), self.user_url)

    def test_should_not_book_a_pool_if_not_authenticated(self):
        response = self.client.post(reverse("booking-list"), self.payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(
            response.data.get("detail").lower(),
            "authentication credentials were not provided.",
        )

    def test_should_not_list_all_bookings_if_user_not_admin(self):
        self.authenticate()
        response = self.client.get(reverse("booking-list"), self.payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(
            response.data.get("detail").lower(),
            "you do not have permission to perform this action.",
        )

    def test_should_not_book_a_pool_with_invalid_urls(self):
        self.payload = {
            "pool": "http://testserver/api/v1/vie",
            "user": "http://testserver/api/v1/vie",
            "start_datetime": self.start,
            "end_datetime": self.end,
        }
        self.authenticate()

        response = self.client.post(reverse("booking-list"), self.payload)

        from_json = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(from_json.get("pool"), ["Invalid hyperlink - No URL match."])
        self.assertEqual(from_json.get("user"), ["Invalid hyperlink - No URL match."])

    def test_should_not_book_a_pool_when_request_has_invalid_dates(self):
        self.payload = {
            "pool": self.payload["pool"],
            "user": self.payload["user"],
            "start_datetime": timezone.now() - timedelta(days=1),
            "end_datetime": timezone.now() - timedelta(days=3),
        }
        self.authenticate()

        response = self.client.post(reverse("booking-list"), self.payload)
        from_json = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(from_json.get("start_datetime"), [START_DATE_PAST_ERROR])
        self.assertEqual(from_json.get("end_datetime"), [END_DATE_PAST_ERROR])

    def test_should_not_book_a_pool_when_start_date_greater_than_end_date(self):
        self.payload = {
            "pool": self.payload["pool"],
            "user": self.payload["user"],
            "start_datetime": timezone.now() + timedelta(days=5),
            "end_datetime": self.payload["end_datetime"],
        }
        self.authenticate()

        response = self.client.post(reverse("booking-list"), self.payload)

        from_json = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(from_json.get("non_field_errors"), [START_DATE_ERROR])

    def test_should_not_book_a_pool_null_payload(self):
        self.payload = {
            "pool": "",
            "user": "",
            "start_datetime": "",
            "end_datetime": "",
        }
        self.authenticate()

        response = self.client.post(reverse("booking-list"), self.payload)
        from_json = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(from_json.get("pool"), ["This field may not be null."])
        self.assertEqual(from_json.get("user"), ["This field may not be null."])
        self.assertEqual(
            from_json.get("start_datetime"),
            [
                "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."
            ],
        )
        self.assertEqual(
            from_json.get("end_datetime"),
            [
                "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."
            ],
        )


class RatingsTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            "myuser", "myemail@test.com", "$#@12D"
        )
        self.user = {
            "username": "nehe",
            "email": "neeh@gmail.com",
            "password": "#$23msnAB",
        }
        self.pool = create_test_pool(user=self.admin)
        self.pool_url = f"http://testserver/api/v1/pools/{self.pool.slug}/"
        self.payload = {"pool": self.pool_url, "value": 4.0}

    def authenticate(self):
        res = self.client.post(reverse("register_user"), self.user)

        self.user_url = (
            f"http://testserver/api/v1/view-users/{res.data.get('user').get('id')}/"
        )

        response = self.client.post(reverse("token_obtain_pair"), self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data.get('access')}"
        )

    def authenticate_admin(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "myuser", "email": "myemail@test.com", "password": "$#@12D"},
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data.get('access')}"
        )

    def test_should_rate_a_swimming_pool(self):
        self.authenticate()

        response = self.client.post(reverse("rating-list"), self.payload)
        from_json = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(from_json.get("pool"), self.pool_url)
        self.assertEqual(from_json.get("user"), self.user_url)
        self.assertEqual(from_json.get("value"), f"{self.payload.get('value')}")

    def test_should_not_rate_a_pool_wih_invalid_url(self):
        self.authenticate()

        self.payload["pool"] = "http://testserver/api/v1/pools/1212"

        response = self.client.post(reverse("rating-list"), self.payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get("pool")[0].lower(), "invalid hyperlink - no url match."
        )

    def test_should_not_rate_pool_invalid_rating1(self):
        """
        Should not rate a swimming pool
        when a rating's value is greater than 5
        """
        self.authenticate()

        self.payload["value"] = 6.0

        response = self.client.post(reverse("rating-list"), self.payload)
        from_json = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            from_json.get("value"), ["Ensure this value is less than or equal to 5.0."]
        )

    def test_should_not_rate_pool_invalid_rating2(self):
        """
        Should not rate a swimming pool
        when a rating's value is less than 0
        """
        self.authenticate()

        self.payload["value"] = -1.0

        response = self.client.post(reverse("rating-list"), self.payload)

        from_json = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            from_json.get("value"),
            ["Ensure this value is greater than or equal to 0.0."],
        )

    def test_should_not_rate_pool_with_invalid_payload(self):
        """
        Should not rate a swimming pool
        when a rating's value is not a string and pool to be rated
        is not given
        """
        self.authenticate()

        self.payload = {"pool": "", "value": ""}

        response = self.client.post(reverse("rating-list"), self.payload)

        from_json = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(from_json.get("value"), ["A valid number is required."])
        self.assertEqual(from_json.get("pool"), ["This field may not be null."])

    def test_should_list_all_ratings_if_user_is_admin(self):
        self.authenticate_admin()

        self.client.post(reverse("rating-list"), self.payload)

        response = self.client.get(reverse("rating-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 1)
        self.assertIsNone(response.data.get("next"))
        self.assertIsNone(response.data.get("previous"))
        self.assertEqual(len(response.data.get("results")), 1)

    def test_should_not_list_all_ratings_if_user_not_admin(self):
        self.authenticate()

        self.client.post(reverse("rating-list"), self.payload)

        response = self.client.get(reverse("rating-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get("detail"),
            "You do not have permission to perform this action.",
        )
        self.assertEqual(response.data.get("detail").code, "permission_denied")
