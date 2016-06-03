# -*- coding: utf-8 -*-

# imports ####################################################################

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import ugettext_lazy as _

from Crypto.Cipher import AES
import base64
import  string, random

# models #####################################################################


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

    email = models.EmailField(verbose_name=_('Email address'), max_length=255, unique=True)
    nickname = models.CharField(verbose_name=_('Nickname'),max_length=30)
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


CERT_SIZE = 16

# one-liner to sufficiently pad the text to be encrypted
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[:-1]

# the secret key
secret = "ivwx7561u826c8i0"

# create a cipher object using the secret key
cipher = AES.new(secret)

from polls.models import VotingPoll

class WhaleUserAnomymous(models.Model):
    certificat = models.CharField(max_length=100)
    email = models.EmailField( max_length=255)
    poll = models.ForeignKey(VotingPoll, on_delete=models.CASCADE)

    @staticmethod
    def encodeAES(s, c=cipher):
        return base64.b64encode(c.encrypt(pad(s)))

    @staticmethod
    def decodeAES(e, c=cipher):
        return unpad(c.decrypt(base64.b64decode(e)))

    @staticmethod
    def id_generator(size=CERT_SIZE, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

