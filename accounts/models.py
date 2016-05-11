# -*- coding: utf-8 -*-

# imports ####################################################################

from django.db import models
from django.contrib.auth.models import User

class WhaleUser(models.Model):
	user = models.OneToOneField(User)  # La liaison OneToOne vers le modèle User
	
	def __str__(self):
		return "WhaleUser {0}".format(self.user.username)
