from django.db import models
from sites.models import Site, Subcontractor

class Worker(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    joining_date = models.DateField()
    daily_wage = models.DecimalField(max_digits=10, decimal_places=2)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='workers')
    
    # ===== NEW: Subcontractor =====
    subcontractor = models.ForeignKey(Subcontractor, on_delete=models.SET_NULL, null=True, blank=True, related_name='workers')
    
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
    
    # ===== NEW: Extra wage for far sites =====
    extra_wage = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Extra amount for far site (e.g., 150)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['worker', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.worker.name} - {self.date} - {self.status}"

class Payroll(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='payrolls')
    month = models.DateField()
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

class WorkLog(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='work_logs')
    date = models.DateField(auto_now_add=True)
    work_done = models.TextField()
    pending_work = models.TextField(blank=True)
    
    # ===== NEW: Workers who worked =====
    workers = models.ManyToManyField(Worker, related_name='work_logs', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def worker_count(self):
        return self.workers.count()
    
    def __str__(self):
        return f"{self.site.name} - {self.date}"
    
    class Meta:
        ordering = ['-date']

class IncomingPayment(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='incoming_payments')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, help_text="e.g., 1st installment, completion payment, etc.")
    received_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.site.name} - ₹{self.amount} - {self.received_date}"
    
    class Meta:
        ordering = ['-received_date']