from django.db import models

class Contractor(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Site(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('completed', 'Completed'),
    ]
    
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # ===== NEW: Measurements =====
    cubic_feet = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="CFt")
    square_feet = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="SFt")
    running_feet = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="RFt")
    
    # ===== NEW: Agreement =====
    agreement_file = models.FileField(upload_to='agreements/', blank=True, null=True)
    agreement_date = models.DateField(blank=True, null=True)
    agreement_party = models.CharField(max_length=300, blank=True, help_text="Who is giving the contract")
    
    # ===== NEW: Contractor =====
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True, blank=True, related_name='sites')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class Subcontractor(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='subcontractors')
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='subcontractors')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.site.name}"
