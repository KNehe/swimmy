from django.db import models
from django.template.defaultfilters import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """ Re-define django's User model """
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    def __str__(self) -> str:
        return self.username


class Pool(models.Model):
    """
    Defines the attributes and database fields of a swimming pool
    """
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=100)
    day_price = models.DecimalField(decimal_places=1, max_digits=3)
    thumbnail_url = models.URLField(max_length=300, null=True, blank=True)
    image_url = models.URLField(max_length=300, null=True, blank=True)
    width = models.DecimalField(decimal_places=1, max_digits=3)
    length = models.DecimalField(decimal_places=1, max_digits=3)
    depth_shallow_end = models.DecimalField(decimal_places=1, max_digits=2)
    depth_deep_end = models.DecimalField(decimal_places=1, max_digits=2)
    maximum_people = models.IntegerField()
    slug = models.SlugField(max_length=100, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='related_by_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='updated_by_user', blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.generate_slug()
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        if hasattr(self, '_average_value'):
            return self._average_value
        return self.rating.aggregate(Avg('value'))['value__avg']

    def generate_slug(self):
        self.slug = slugify(self.name)


class Booking(models.Model):
    """
    Defines attributes and database fields contained
    by a booking of a swimming pool by a user
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='booked_by_user')
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE,
                             related_name='booked_swimming_pools')
    # total_amount = day price * number of days(start day - end day)
    # It should be auto-calculated as shown below in save() method
    total_amount = models.DecimalField(decimal_places=2, max_digits=5,
                                       blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    slug = models.SlugField(max_length=100, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='booking_updated_by',
                                   blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f'Booked by {self.user}'

    def save(self, *args, **kwargs):
        self.calculate_total()
        self.generate_slug()
        super().save(*args, **kwargs)

    def calculate_total(self):
        number_of_days = (self.end_datetime - self.start_datetime).days
        self.total_amount = number_of_days * self.pool.day_price\
            if number_of_days > 0 else self.pool.day_price

    def generate_slug(self):
        self.slug = slugify(f'{self.pool} booked by {self.user}')


class Rating(models.Model):
    """Defines attributes and database fields of a
       swimming pool's rating by a user
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='rated_by')
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE,
                             related_name='rating')
    value = models.DecimalField(decimal_places=1, max_digits=2,
                                validators=[MinValueValidator(0.0),
                                            MaxValueValidator(5.0)])
    slug = models.SlugField(max_length=100, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f'Rated by: {self.user}'

    def save(self, *args, **kwargs):
        self.generate_slug()
        super().save(*args, **kwargs)

    def generate_slug(self):
        self.slug = slugify(f'{self.pool} rated by {self.user}')


class FileUpload(models.Model):
    file_name = models.CharField(max_length=50)
    file = models.FileField(upload_to='media/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.file_name}'
