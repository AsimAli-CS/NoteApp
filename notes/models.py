from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Note(models.Model):

    title = models.CharField(max_length=255)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    share_with = models.ManyToManyField(User, related_name="share_notes", blank=True)
    archive = models.BooleanField(default=False)
    archive_date = models.DateTimeField(auto_now_add=True() + timedelta(days=7))
    
    
    def __str__(self):
        return self.title
    
class Comment(models.Model):

    text = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    note = models.ForeignKey(Note,on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return self.user.email
    
class VersionControl(models.Model):
    
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="changed_notes") 
    note = models.ForeignKey(Note,on_delete=models.CASCADE, related_name="history") 
    text = models.CharField(max_length=255) 
    title = models.CharField(max_length=255) 
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
