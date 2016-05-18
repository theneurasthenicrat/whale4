# -*- coding: utf-8 -*-

# imports ####################################################################

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import ugettext_lazy as _
import uuid
# models #####################################################################

class User(models.Model):
    id = models.CharField(max_length=100, primary_key=True, default=uuid.uuid4, editable=False)
    nickname = models.CharField(max_length=50)

class WhaleUserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None):
        user = self.model(email=self.normalize_email(email), nickname=nickname)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password,):
        user = self.model(email=self.normalize_email(email), nickname=nickname,password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class WhaleUser(AbstractBaseUser):

    email = models.EmailField(verbose_name=_('email address'), max_length=255, unique=True)
    nickname = models.CharField(verbose_name=_('nickname'),max_length=30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False) 

    objects = WhaleUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def get_full_name(self):
        return self.nickname

    def get_short_name(self):
        return self.nickname

    def __str__(self):             
        return self.nickname

