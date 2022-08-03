# -*- coding: utf-8 -*-

# imports ####################################################################

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel
try:
    from polymorphic.managers import PolymorphicManager
except ImportError:
    from polymorphic.manager import PolymorphicManager
import uuid
from Crypto.Cipher import AES
import base64
import string, random
import whale4.settings



# decoder ####################################################################
CERT_SIZE = 16

# one-liner to sufficiently pad the text to be encrypted
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[:-1]

# create a cipher object using the secret key
cipher = AES.new(whale4.settings.SECRET_KEY.encode('utf-8'), AES.MODE_ECB)


# models #####################################################################


class User(PolymorphicModel):

    id = models.CharField(max_length=100, primary_key=True, default=uuid.uuid4, editable=False)
    nickname = models.CharField(verbose_name=_('Nickname *'), max_length=30)


class WhaleUserManager(PolymorphicManager,BaseUserManager):
    def create_user(self, email, nickname, password=None,*args,**kwargs):
        user = self.model(email=self.normalize_email(email), nickname=nickname,*args,**kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password,):
        user = self.model(email=self.normalize_email(email), nickname=nickname,password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class WhaleUser(User, AbstractBaseUser):
    objects = WhaleUserManager()
    email = models.EmailField(verbose_name=_('Email address *'), max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def get_full_name(self):
        return self.nickname

    def get_short_name(self):
        return self.nickname

    def __str__(self):             
        return self.nickname


from polls.models import VotingPoll


class UserAnonymous(User):
    poll = models.ForeignKey(VotingPoll, on_delete=models.CASCADE)

    @staticmethod
    def nickname_generator(poll):
        user = UserAnonymous.objects.filter(poll_id=poll).count() + 1
        return 'Anonymous' + str(user)


class WhaleUserAnonymous(UserAnonymous):
    certificate = models.CharField(max_length=100)
    email = models.EmailField(verbose_name=_('Email address'), max_length=255)

    @staticmethod
    def encodeAES(s, c=cipher):
        return base64.b64encode(c.encrypt(pad(s).encode('utf-8')))

    @staticmethod
    def decodeAES(e, c=cipher):
        return unpad(c.decrypt(base64.b64decode(e)))

    @staticmethod
    def id_generator(size=CERT_SIZE, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))




