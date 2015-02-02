from django.shortcuts import render
import datetime
from payroll_app.models import Employer, Employee, Job, BonusPay


# Create your views here.
def index(request):
	# employer1 = Employer(employer_id="12468",employer_name="Amazon", address="265 Lytton Ave.", pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), hash_key="HASHVALUE1")
	# employer2 = Employer(employer_id="13492",employer_name="Microsoft", address="610 Mayfield Ave", pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), hash_key="HASHVALUE2")
	# employee1 = Employee(employee_id="78932",employer_id="12468", employee_name = "Naveen Krishnamurthi", vacation_hours = 6.00, vacation_pay_rate = 60.00, sick_hours = 12.00, sick_pay_rate = 60.00, vacation_accrual_rate = 0.01, address="12795 Calle De La Siena, San Diego CA, 92130")
	# employee2 = Employee(employee_id="78777",employer_id="13492", employee_name = "Danial Shakeri", vacation_hours = 8.00, vacation_pay_rate = 62.00, sick_hours = 13.00, sick_pay_rate = 64.00, vacation_accrual_rate = 0.02, address="265 Westfield Ave., San Diego CA, 92130")
	# employee3 = Employee(employee_id="78412",employer_id="13492", employee_name = "Kevin Miller", vacation_hours = 10.00, vacation_pay_rate = 65.00,  sick_hours = 14.00, sick_pay_rate = 65.00, vacation_accrual_rate = 0.01, address="710 New York St., New York NY, 94099")
	# job1 = Job(job_id="8933", employee_id="78932", base_rate = 65.00, incremental_hours_1=2.50, incremental_hours_2=0.00, job_title = "Designer")
	# job2 = Job(job_id="7412", employee_id="78932", base_rate = 70.00, incremental_hours_1=1.00, incremental_hours_2=0.00, job_title = "Engineer I")
	# job3 = Job(job_id="8935", employee_id="78777", base_rate = 68.00, incremental_hours_1=2.50, incremental_hours_2=2.00, job_title = "Engineer II")
	# job4 = Job(job_id="8936", employee_id="78412", base_rate = 67.00, incremental_hours_1=2.50, incremental_hours_2=0.00, job_title = "Engineer II")
	# bp1 = BonusPay(bonus_id="1234", employee_id="78777", amount = 1000.01, pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), date_given=datetime.datetime(2013, 12, 25, 17, 18, 40))
	# bp2 = BonusPay(bonus_id="1256", employee_id="78412", amount = 1700.99, pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), date_given=datetime.datetime(2013, 12, 25, 17, 18, 40))
	# employer1.save()
	# employer2.save()
	# employee1.save()
	# employee2.save()
	# employee3.save()
	# job1.save()
	# job2.save()
	# job3.save()
	# job4.save()
	# bp1.save()
	# bp2.save()
	return render(request, 'index.html', {})

def addCompany(request):
    employer_id = request.POST['employer_id']
    employer_name = request.POST['employer_name']
    employer_address = request.POST['employer_address']
    employer_key = request.POST['employer_key']
    employer = Employer(employer_id=employer_id, employer_name=employer_name, address=employer_address, hash_key=employer_key)
    employer.save()
    return HttpResponse("Successfully created entry for %s." % employer_name) 
}

def addEmployee(request):
    employee_id = request.POST['employee_id']
    employer_id = request.POST['employer_id']
    employee_name = request.POST['employee_name']
    employee_address = request.POST['employee_address']
    try:
        vacation_hours = request.POST['vacation_hours']
    except (KeyError, Choice.DoesNotExist):
    try:
        sick_hours = request.POST['sick_hours']
    except (KeyError, Choice.DoesNotExist):
    try:
        vacation_pay_rate = request.POST['vacation_pay_rate']
    except (KeyError, Choice.DoesNotExist):
    try:
        sick_pay_rate = request.POST['sick_pay_rate']
    except (KeyError, Choice.DoesNotExist):
    try:
        vacation_accrual_rate = request.POST['vacation_accrual_rate']
    except (KeyError, Choice.DoesNotExist):
    employee = Employee(employer_id=employer_id, employee_id=employee_id, employee_name=employee_name, address=employee_address, vacation_hours = vacation_hours, vacation_pay_rate = vacation_pay_rate,  sick_hours = sick_hours, sick_pay_rate = sick_pay_rate, vacation_accrual_rate = vacation_accrual_rate)
    employee.save()
    return HttpResponse("Successfully created entry for %s." % employee_name) 
}

def addJob(request):
    job_id = request.POST['job_id']
    employee_id = request.POST['employee_id']
    base_rate = request.POST['base_rate']
    incremental_rate_1 = request.POST['incremental_rate_1']
    incremental_rate_2 = request.POST['incremental_rate_2']
    job_title = request.POST['job_title']
	job = Job(job_id=job_id, employee_id=employee_id, base_rate = base_rate, incremental_hours_1=incremental_hours_1, incremental_hours_2=incremental_hours_2, job_title = job_title)
    job.save()
