from django.db import models

class Worker(models.Model):
    name = models.CharField(max_length = 100)
    phone = models.CharField(max_length = 15)
    joining_date = models.DateField()
    daily_wage = models.DecimalField(max_digits = 10, decimal_places=2)

    def __str__(self):
        return self.name
