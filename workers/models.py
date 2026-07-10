from django.db import models
from sites.models import Site

class Worker(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    joining_date = models.DateField()
    daily_wage = models.DecimalField(max_digits=10, decimal_places=2)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='workers', null=True, blank=True)
    
    def __str__(self):
        return self.name


class Attendance(models.Model):
    ATTENDANCE_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('paid_leave', 'Paid Leave'),
        ('unpaid_leave', 'Unpaid Leave'),
    ]

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES, default='present')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['worker', 'date']  # One attendance per worker per day
        ordering = ['-date']

    def __str__(self):
        return f"{self.worker.name} - {self.date} - {self.status}"
