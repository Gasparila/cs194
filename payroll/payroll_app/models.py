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
	#holiday_hours = models.DecimalField(max_digits = 8, decimal_places = 2)
	#holiday_pay_rate = models.DecimalField(max_digits = 8, decimal_places = 2)
	sick_hours = models.DecimalField(max_digits = 8, decimal_places = 2)
	sick_pay_rate = models.DecimalField(max_digits = 8, decimal_places = 2)
	vacation_accrual_rate = models.DecimalField(max_digits = 8, decimal_places = 2)
	address = models.CharField(max_length=300)

class Job(models.Model):
	job_id = models.CharField(max_length=100)
	employee_id = models.CharField(max_length=100)
	base_rate = models.DecimalField(max_digits = 8, decimal_places = 2)
	incremental_hours_1 = models.DecimalField(max_digits = 8, decimal_places = 2)
	#incremental_name_1 
	incremental_hours_2 = models.DecimalField(max_digits = 8, decimal_places = 2)
	#incremental_name_2 
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
	#holiday_hours_total
	#vacation_hours_total
	#sick_hours_total

	def __str__(self):
		DATE_FORMAT = "%m-%d-%Y" 
		return 'employee_id: %s, job_id: %s, pay_start: %s, pay_end: %s, hours: %s, overtime_hours: %s, incremental_hours_1: %s, incremental_hours_2: %s, incremental_hours_1_and_2: %s, holiday_hours: %s, sick_hours: %s, vacation_hours: %s, holiday_hours_spent: %s, sick_hours_spent: %s, vacation_hours_spent: %s' % (self.employee_id, self.job_id, self.pay_start.strftime(DATE_FORMAT), self.pay_end.strftime(DATE_FORMAT), self.hours, self.overtime_hours, self.incremental_hours_1, self.incremental_hours_2, self.incremental_hours_1_and_2, self.holiday_hours, self.sick_hours, self.vacation_hours, self.holiday_hours_spent, self.sick_hours_spent, self.vacation_hours_spent)




