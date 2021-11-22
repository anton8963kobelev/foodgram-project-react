from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractUser):
    first_name = models.CharField('first name', max_length=150)  # чтобы null
    last_name = models.CharField('last name', max_length=150)  # и blank
    email = models.EmailField('email address')  # были False

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = (models.ForeignKey(User, on_delete=models.CASCADE,
            related_name='follower'))
    author = (models.ForeignKey(User, on_delete=models.CASCADE,
              related_name='following'))

    class Meta:
        models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_following'
        )
