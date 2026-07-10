from django.db import models

# Create your models here.

class Site(models.Model):
    STATUS_CHOICES = [
            ('active','Active'),
            ('inactive','Inactive'),
            ('completed','Completed'),
    ]

    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name


    class Meta:
        ordering = ['-created_at']
