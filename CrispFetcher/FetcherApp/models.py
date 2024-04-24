from django.db import models
from django.contrib.auth.models import User


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    old_XML_path = models.TextField(max_length=3000, blank=True)
    new_XML_path = models.TextField(max_length=3000, blank=True)

    old_XML_content = models.TextField(max_length=300000, blank=True)
    new_XML_content = models.TextField(max_length=300000, blank=True)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modidied = models.DateTimeField(blank = True)