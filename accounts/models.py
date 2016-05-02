# -*- coding: utf-8 -*-

# imports ####################################################################

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager

# models #####################################################################

class WhaleUserManager(BaseUserManager):
    def create_user(self, email, password, nickname, **kwargs):
        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
            is_active=True,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, nickname, **kwargs):
        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
            is_staff=True,
            is_admin=True,
            is_active=True,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

class WhaleUser(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'

    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    objects = WhaleUserManager()
    
    def get_full_name(self):
        return self.nickname
    def get_short_name(self):
        return self.nickname
