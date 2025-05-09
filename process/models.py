# process/models.py

from django.db import models

# Create your models here.

class Process(models.Model):
    email = models.CharField(max_length=150, unique=True)
    message = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        ordering = ('email',)

    def __str__(self):
        return self.email

class Message(models.Model):
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.email}: {self.message[:50]}'

