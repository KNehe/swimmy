from django.test import TestCase
from django.utils import timezone

from datetime import timedelta

from pools.models import Booking, Rating
from .helpers import create_test_user, create_test_pool


class AverageRatingTest(TestCase):
    def test_average_rating(self):
        """
        Should calculate correct average rating of a pool
        """
        user_1 = create_test_user()
        user_2 = create_test_user(email='doe@gmail.com')

        pool = create_test_pool(user=user_1)

        Rating.objects.create(user=user_1, pool=pool, value=2.5)
        Rating.objects.create(user=user_2, pool=pool, value=3.5)

        self.assertEqual(pool.average_rating, 3.0)


class BookingTest(TestCase):
    def test_total_amount(self):
        """
        Should calculate correct total amount when
        the number of days (difference between startdateime and enddatetime)
        is greater than 0
        """
        user = create_test_user(email='doe2@gmail.com')

        # pool's day_price=10.0
        pool = create_test_pool(user=user)
        start = timezone.now()
        end = timezone.now() + timedelta(days=2)

        booking = Booking.objects.create(user=user, pool=pool,
                                         start_datetime=start,
                                         end_datetime=end)
        expected_amount = (end - start).days * pool.day_price
        self.assertEqual(booking.total_amount, expected_amount)

    def test_total_amount_same_day(self):
        """
        Should calculate correct total amount when
        the start and end day is the same
        Total amount should equal a pool day price
        """
        user = create_test_user(email='doe3@gmail.com')

        # pool's day_price=10.0
        pool = create_test_pool(user=user)
        start = timezone.now()
        end = timezone.now() + timedelta(hours=4)

        booking = Booking.objects.create(user=user, pool=pool,
                                         start_datetime=start,
                                         end_datetime=end)
        self.assertEqual(booking.total_amount, pool.day_price)


# THE COMMENTED TESTS BELOW ARE NOT NECESSARY
# SINCE DJANGO HAS ALREADY ENOUGH TESTS
# THEY ARE FOR LEARNING PURPOSES *ONLY*!
# TESTS SHOULD ONLY COVER YOUR LOGIC

# class PoolModelTests(TestCase):
#     """Tests for the custom user model"""

#     def test_create_pool(self):
#         """
#         Should create a swimming pool with all fields
#         """
#         user = create_test_user()
#         pool = Pool.objects.create(created_by=user, name='Nehe Ducks',
#                                    location='Naboa road Mbale uganda',
#                                    day_price=10.5,
#                                    thumbnail_url='https://aws.s3/pic.png"',
#                                    width=4.0,
#                                    length=8.2,
#                                    depth_shallow_end=1.2,
#                                    depth_deep_end=3.0,
#                                    maximum_people=15,
#                                    updated_by=user)
#         self.assertEqual(pool.name, 'Nehe Ducks')
#         self.assertEqual(pool.location, 'Naboa road Mbale uganda')
#         self.assertEqual(pool.depth_shallow_end, 1.2)
#         self.assertEqual(pool.thumbnail_url, 'https://aws.s3/pic.png"')
#         self.assertEqual(pool.maximum_people, 15)
#         self.assertEqual(pool.day_price, 10.5)
#         self.assertEqual(pool.length, 8.2)
#         self.assertEqual(pool.updated_by, user)
#         self.assertEqual(pool.created_by, user)
#         self.assertEqual(pool.slug, 'nehe-ducks')

#     def test_do_not_create_pool(self):
#         """
#         Should raise IntegrityError when any required field is missing
#         """
#         with self.assertRaises(IntegrityError):
#             Pool.objects.create()

#     def test_access_none_atribute(self):
#         """
#         Should raise AttributeError when attribute doesn't exist
#         """
#         pool = create_test_pool()
#         with self.assertRaises(AttributeError):
#             self.assertEqual(pool.unkown_attribute, 'unknown')


# class BookingModelTests(TestCase):
#     """
#     Contains automated tests for Booking model
#     """

#     def test_create_booking(self):
#         """
#         Should save a booking made by a user
#         Total amount auto-calculated
#         """
#         start = timezone.now()
#         end = timezone.now() + timedelta(days=2)

#         user = create_test_user(email='johndoe@gmail.com')
#         pool = create_test_pool()
#         booking = Booking.objects.create(user=user, start_datetime=start,
#                                          end_datetime=end,
#                                          pool=pool)

#         # totoal = pool.day_price (10.0) * days (start-end)
#         self.assertEqual(booking.total_amount, 20.0)
#         self.assertEqual(booking.pool, pool)
#         self.assertEqual(booking.user, user)
#         self.assertEqual(booking.start_datetime, start)
#         self.assertEqual(booking.end_datetime, end)

#     def test_not_create_booking_with_no_dates(self):
#         """
#         Should not create booking when start or end date are missing
#         """
#         with self.assertRaises(TypeError):
#             """
#             Raises TypeError because start_datetime is None
#             """
#             Booking.objects.create()

#     def test_not_create_booking_with_dates(self):
#         """
#         Should raise an Attribute error when
#         only start and end date are given
#         """
#         with self.assertRaises(AttributeError):
#             start = timezone.now()
#             end = timezone.now() + timedelta(days=2)

#             Booking.objects.create(start_datetime=start, end_datetime=end)
