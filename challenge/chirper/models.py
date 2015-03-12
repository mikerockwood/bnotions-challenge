from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class UserProfile(AbstractUser):
  following = models.ManyToManyField('self', related_name='followers', symmetrical=False)

class Chirp(models.Model):
  author = models.ForeignKey(UserProfile, related_name='chirps', null=True)
  time_posted = models.DateTimeField(null=True)
  text = models.CharField(max_length=140)
