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


class Payroll(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='payrolls')
    month = models.DateField()  # First day of month
    total_days = models.IntegerField(default=30)
    working_days = models.IntegerField()
    paid_leaves = models.IntegerField(default=0)
    unpaid_leaves = models.IntegerField(default=0)
    daily_wage = models.DecimalField(max_digits=10, decimal_places=2)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['worker', 'month']
        ordering = ['-month']

    def __str__(self):
        return f"{self.worker.name} - {self.month.strftime('%B %Y')}"


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('material', 'Material'),
        ('food', 'Food'),
        ('fuel', 'Fuel'),
        ('equipment', 'Equipment'),
        ('other', 'Other'),
    ]

    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.site.name} - {self.category} - ₹{self.amount}"
