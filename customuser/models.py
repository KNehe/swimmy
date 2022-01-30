from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """ Re-define django's User model """
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    def __str__(self) -> str:
        return self.username
