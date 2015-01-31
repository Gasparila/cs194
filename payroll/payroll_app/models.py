from django.db import models

# Create your models here.
class Employer(models.Model):
	employer_id = models.CharField(max_length=100)
	employer_name = models.CharField(max_length=100)
	address = models.CharField(max_length=100)
	pay_start = models.DateTimeField()
	pay_end = models.DateTimeField()
	hash_key = models.CharField(max_length=100)

class Employee(models.Model):
	employee_id = models.CharField(max_length=100)
	employer_id = models.CharField(max_length=100)
	employee_name = models.CharField(max_length=100)
	vacation_hours = models.DecimalField(max_digits = 8, decimal_places = 2)
	vacation_pay_rate = models.DecimalField(max_digits = 8, decimal_places = 2)
	sick_hours = models.DecimalField(max_digits = 8, decimal_places = 2)
	sick_pay_rate = models.DecimalField(max_digits = 8, decimal_places = 2)
	vacation_accrual_rate = models.DecimalField(max_digits = 8, decimal_places = 2)
	address = models.CharField(max_length=300)

class Job(models.Model):
	job_id = models.CharField(max_length=100)
	employee_id = models.CharField(max_length=100)
	base_rate = models.DecimalField(max_digits = 8, decimal_places = 2)
	incremental_hours_1 = models.DecimalField(max_digits = 8, decimal_places = 2)
	incremental_hours_2 = models.DecimalField(max_digits = 8, decimal_places = 2)
	job_title =  models.CharField(max_length=100)

class BonusPay(models.Model):
	bonus_id = models.CharField(max_length=100)
	employee_id = models.CharField(max_length=100)
	amount = models.CharField(max_length=100)
	pay_start = models.DateTimeField()
	pay_end = models.DateTimeField()
	date_given = models.DateTimeField()

class PayPeriod(models.Model):
	employee_id = models.CharField(max_length=100)
	job_id = models.CharField(max_length=100)
	pay_start = models.DateTimeField()
	pay_end = models.DateTimeField()
	hours = models.DecimalField(max_digits = 8, decimal_places = 2)
	overtime_hours = models.DecimalField(max_digits = 8, decimal_places = 2)
	incremental_hours_1 = models.DecimalField(max_digits = 8, decimal_places = 2)
	incremental_hours_2 = models.DecimalField(max_digits = 8, decimal_places = 2)
	incremental_hours_1_and_2 = models.DecimalField(max_digits = 8, decimal_places = 2)
	incremental_hours_2 = models.DecimalField(max_digits = 8, decimal_places = 2)
	holiday_hours = models.DecimalField(max_digits = 8, decimal_places = 2)
	sick_hours = models.DecimalField(max_digits = 8, decimal_places = 2)
	vacation_hours = models.DecimalField(max_digits = 8, decimal_places = 2)
	holiday_hours_spent = models.DecimalField(max_digits = 8, decimal_places = 2)
	sick_hours_spent = models.DecimalField(max_digits = 8, decimal_places = 2)
	vacation_hours_spent = models.DecimalField(max_digits = 8, decimal_places = 2)





