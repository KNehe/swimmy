from datetime import date
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from datetime import timedelta

from customuser.models import User
from restful.models import Booking, Pool


def create_test_user(email='nehe@gmail.com'):
    """
    Creates and returns a user object to be used in different unit tests
    """
    user = User.objects.create(email=email,
                               password='123Deaally@',
                               username=email)
    return user


def create_test_pool():
    """
    Creates and returns a swimmming pool
    object to be used in different unit tests
    """
    user = create_test_user()
    pool = Pool.objects.create(created_by=user, name='Nehe Ducks',
                               location='Naboa road Mbale uganda',
                               day_price=10.0,
                               thumbnail_url="https://aws.s3/images/pic.png",
                               image_url="https://aws.s3/images/pic.png",
                               width=4.0,
                               length=8.2,
                               depth_shallow_end=1.2,
                               depth_deep_end=3.0,
                               maximum_people=15,
                               updated_by=user)
    return pool


class PoolModelTests(TestCase):
    """Tests for the custom user model"""

    def test_create_pool(self):
        """
        Should create a swimming pool with all fields
        """
        user = create_test_user()
        pool = Pool.objects.create(created_by=user, name='Nehe Ducks',
                                   location='Naboa road Mbale uganda',
                                   day_price=10.5,
                                   thumbnail_url='https://aws.s3/pic.png"',
                                   width=4.0,
                                   length=8.2,
                                   depth_shallow_end=1.2,
                                   depth_deep_end=3.0,
                                   maximum_people=15,
                                   updated_by=user)
        self.assertEqual(pool.name, 'Nehe Ducks')
        self.assertEqual(pool.location, 'Naboa road Mbale uganda')
        self.assertEqual(pool.depth_shallow_end, 1.2)
        self.assertEqual(pool.thumbnail_url, 'https://aws.s3/pic.png"')
        self.assertEqual(pool.maximum_people, 15)
        self.assertEqual(pool.day_price, 10.5)
        self.assertEqual(pool.length, 8.2)
        self.assertEqual(pool.updated_by, user)
        self.assertEqual(pool.created_by, user)
        self.assertEqual(pool.slug, 'nehe-ducks')

    def test_do_not_create_pool(self):
        """
        Should raise IntegrityError when any required field is missing
        """
        with self.assertRaises(IntegrityError):
            Pool.objects.create()

    def test_access_none_atribute(self):
        """
        Should raise AttributeError when attribute doesn't exist
        """
        pool = create_test_pool()
        with self.assertRaises(AttributeError):
            self.assertEqual(pool.unkown_attribute, 'unknown')


class BookingModelTests(TestCase):
    """
    Contains automated tests for Booking model
    """

    def test_create_booking(self):
        """
        Should save a booking made by a user
        Total amount auto-calculated
        """
        start = timezone.now()
        end = timezone.now() + timedelta(days=2)

        user = create_test_user(email='johndoe@gmail.com')
        pool = create_test_pool()
        booking = Booking.objects.create(user=user, start_datetime=start,
                                         end_datetime=end,
                                         pool=pool)

        # totoal = pool.day_price (10.0) * days (start-end)
        self.assertEqual(booking.total_amount, 20.0)
        self.assertEqual(booking.pool, pool)
        self.assertEqual(booking.user, user)
        self.assertEqual(booking.start_datetime, start)
        self.assertEqual(booking.end_datetime, end)

    def test_not_create_booking_with_no_dates(self):
        """
        Should not create booking when start or end date are missing
        """
        with self.assertRaises(TypeError):
            """
            Raises TypeError because start_datetime is None
            """
            Booking.objects.create()

    def test_not_create_booking_with_dates(self):
        """
        Should raise an Attribute error when only start and end date are given
        """
        with self.assertRaises(AttributeError):
            start = timezone.now()
            end = timezone.now() + timedelta(days=2)

            Booking.objects.create(start_datetime=start, end_datetime=end)
