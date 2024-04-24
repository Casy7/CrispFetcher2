from django.db import models
from django.contrib.auth.models import User


class OpenedEditor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    old_XML_path = models.TextField(max_length=3000, blank=True)
    new_XML_path = models.TextField(max_length=3000, blank=True)
    
    XMLs_editor_data = models.TextField(max_length=3000000, blank = True)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(blank = True)