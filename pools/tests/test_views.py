from django.urls import reverse
from rest_framework.test import APITestCase

from .helpers import create_test_pool, create_test_user
import json
from django.utils import timezone
from datetime import timedelta
from pools.errors import END_DATE_PAST_ERROR, START_DATE_ERROR, START_DATE_PAST_ERROR


class BookingTests(APITestCase):
    def setUp(self):
        self.pool = create_test_pool()
        self.user = create_test_user(email="nehe2@gmail.com")
        self.password = "123Deaally"
        self.email = "nehe2@gmail.com"
        self.pool_url = f"http://testserver/api/v1/pools/{self.pool.slug}/"
        self.user_url = f"http://testserver/api/v1/view-users/{self.user.id}/"
        self.url = "http://testserver/api/v1/bookings/"
        self.start = timezone.now() + timedelta(days=1)
        self.end = timezone.now() + timedelta(days=3)
        self.payload = {
            "pool": self.pool_url,
            "user": self.user_url,
            "start_datetime": self.start,
            "end_datetime": self.end,
        }

    def test_book_a_pool(self):
        """
        Should book a swimming pool
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 201)

        from_json = json.loads(response.content)

        self.assertEqual(from_json.get("pool_name"), self.pool.name)
        self.assertEqual(
            from_json.get("start_datetime"),
            self.start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        self.assertEqual(
            from_json.get("end_datetime"), self.end.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        self.assertEqual(from_json.get("pool"), self.pool_url)
        self.assertEqual(from_json.get("user"), self.user_url)

    def test_book_pool_not_authenticated(self):
        """
        Should not create a booking if user is not autheticated
        """
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 401)
        from_json = json.loads(response.content)
        self.assertEqual(
            from_json.get("detail"), "Authentication credentials were not provided."
        )

    def test_book_a_pool_invalid_url(self):
        """
        Should not book a swimming  when request has invalid urls
        """
        self.payload = {
            "pool": "http://testserver/api/v1/vie",
            "user": "http://testserver/api/v1/vie",
            "start_datetime": self.start,
            "end_datetime": self.end,
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 400)

        from_json = json.loads(response.content)
        self.assertEqual(from_json.get("pool"), ["Invalid hyperlink - No URL match."])
        self.assertEqual(from_json.get("user"), ["Invalid hyperlink - No URL match."])

    def test_book_a_pool_invalid_dates(self):
        """
        Should not book a swimming  when request has invalid dates
        """
        self.payload = {
            "pool": self.payload["pool"],
            "user": self.payload["user"],
            "start_datetime": timezone.now() - timedelta(days=1),
            "end_datetime": timezone.now() - timedelta(days=3),
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 400)

        from_json = json.loads(response.content)
        self.assertEqual(from_json.get("start_datetime"), [START_DATE_PAST_ERROR])
        self.assertEqual(from_json.get("end_datetime"), [END_DATE_PAST_ERROR])

    def test_book_a_pool_invalid_start_date(self):
        """
        Should not book a swimming  when start date is greater than end date
        """
        self.payload = {
            "pool": self.payload["pool"],
            "user": self.payload["user"],
            "start_datetime": timezone.now() + timedelta(days=5),
            "end_datetime": self.payload["end_datetime"],
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 400)

        from_json = json.loads(response.content)
        self.assertEqual(from_json.get("non_field_errors"), [START_DATE_ERROR])

    def test_book_a_pool_null_payload(self):
        """
        Should not book a swimming
        when request has empty payload
        """
        self.payload = {
            "pool": "",
            "user": "",
            "start_datetime": "",
            "end_datetime": "",
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 400)

        from_json = json.loads(response.content)
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
        self.user = create_test_user(email="doe@gmail.com")
        self.pool = create_test_pool(user=self.user)
        self.url = "http://testserver/api/v1/ratings/"
        self.pool_url = f"http://testserver/api/v1/pools/{self.pool.slug}/"
        self.user_url = f"http://testserver/api/v1/view-users/{self.user.id}/"
        self.payload = {"pool": self.pool_url, "value": 4.0}

    def test_rate_pool(self):
        """
        Should rate a swimming pool
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 201)

        from_json = json.loads(response.content)
        self.assertEqual(from_json.get("pool"), self.pool_url)
        self.assertEqual(from_json.get("user"), self.user_url)
        self.assertEqual(from_json.get("value"), f"{self.payload.get('value')}")

    def test_rate_pool_invalid_url(self):
        """
        Should not rate a swimming pool when a pool's url is invalid
        """
        self.client.force_authenticate(user=self.user)
        self.payload = {"pool": "http://testserver/api/v1/pools/1212", "value": 4.0}

        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 400)

        from_json = json.loads(response.content)
        self.assertEqual(from_json.get("pool"), ["Invalid hyperlink - No URL match."])

    def test_rate_pool_invalid_value1(self):
        """
        Should not rate a swimming pool
        when a rating's value is greater than 5
        """
        self.client.force_authenticate(user=self.user)
        self.payload = {"pool": self.pool_url, "value": 6.0}

        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 400)

        from_json = json.loads(response.content)
        self.assertEqual(
            from_json.get("value"), ["Ensure this value is less than or equal to 5.0."]
        )

    def test_rate_pool_invalid_value2(self):
        """
        Should not rate a swimming pool
        when a rating's value is less than 0
        """
        self.client.force_authenticate(user=self.user)
        self.payload = {"pool": self.pool_url, "value": -1.0}

        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 400)

        from_json = json.loads(response.content)
        self.assertEqual(
            from_json.get("value"),
            ["Ensure this value is greater than or equal to 0.0."],
        )

    def test_rate_pool_invalid_payload(self):
        """
        Should not rate a swimming pool
        when a rating's value is not a string and pool to be rated
        is not given
        """
        self.client.force_authenticate(user=self.user)
        self.payload = {"pool": "", "value": ""}

        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 400)

        from_json = json.loads(response.content)
        self.assertEqual(from_json.get("value"), ["A valid number is required."])
        self.assertEqual(from_json.get("pool"), ["This field may not be null."])


class PoolsTest(APITestCase):
    def setUp(self):
        self.pool = create_test_pool()

    def test_get_pools(self):
        """
        Should return paginated response of pools
        """
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
