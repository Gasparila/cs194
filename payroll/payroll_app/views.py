from django.shortcuts import render
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
from payroll_app.models import Employer, Employee, Job, BonusPay, PayPeriod


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
	#PayPeriod.objects.all().delete()
	#payPeriod1 = PayPeriod(employee_id="78777", job_id="8935", pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), hours = 40, overtime_hours = 2, incremental_hours_1 = 0, incremental_hours_2 = 0, incremental_hours_1_and_2 = 2, holiday_hours = 10, sick_hours = 12, vacation_hours = 12, holiday_hours_spent = 0, sick_hours_spent = 2, vacation_hours_spent = 0)
	#payPeriod1.save()
	employer_id = "13492"
	employee_id = "78777"
	employer = Employer.objects.get(employer_id = employer_id)
	if employer_id ==  employer.employer_id: 
		payPeriod1 = PayPeriod.objects.all().filter(employee_id=employee_id)
		employee = Employee.objects.all().get(employee_id = employee_id)
		jobs = Job.objects.all().filter(employee_id = employee_id)
		print payPeriod1
		return render(request, 'index.html', {'payperiods' : payPeriod1, 'employer' : employer, 'employee' : employee, 'jobs' : jobs })
	

	return render(request, 'index.html', {})

def checkEmployer(employer_id, employer_password):
    #TODO: Implement this
    return true

#TODO: remove this since we should manually add companies
@csrf_exempt
def addCompany(request):
    if request.method == 'POST':
        print request.body
        json_data = json.loads(request.body)
        try:
            employer_id = json_data['employer_id']
            employer_name = json_data['employer_name']
            employer_address = json_data['employer_address']
            employer_key = json_data['employer_key']
        except KeyError:
            raise Http404("Employer info not found")
        employer = Employer(employer_id=employer_id, employer_name=employer_name, address=employer_address, hash_key=employer_key)
        employer.save()
        return HttpResponse("Successfully created entry for %s." % employer_name) 
    raise Http404("Error, request wasn't POST")

@csrf_exempt
def addEmployee(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        try:
            employee_id = json_data['employee_id']
            employer_id = json_data['employer_id']
            employer_password = json_data['employer_key']
        except KeyError:
            raise Http404("EmployeeID, or employer info not found")
        if not checkEmployer(employer_id, employer_password):
            raise Http404("Invalid Employer ID/Key")
        try:
            employee_name = json_data['employee_name']
            employee_address = json_data['employee_address']
        except KeyError:
            raise Http404("Employee info not found")
        try:
            vacation_hours = json_data['vacation_hours']
        except KeyError:
            vacation_hours = 0 
        try:
            sick_hours = json_data['sick_hours']
        except KeyError:
            sick_hours = 0
        try:
            vacation_pay_rate = json_data['vacation_pay_rate']
        except KeyError:
            vacation_pay_rate = 0  
        try:
            sick_pay_rate = json_data['sick_pay_rate']
        except KeyError:
            sick_pay_rate = 0
        try:
            vacation_accrual_rate = json_data['vacation_accrual_rate']
        except KeyError:
            vacation_accrual_rate = 0    
        employee = Employee(employer_id=employer_id, employee_id=employee_id, employee_name=employee_name, address=employee_address, vacation_hours = vacation_hours, vacation_pay_rate = vacation_pay_rate,  sick_hours = sick_hours, sick_pay_rate = sick_pay_rate, vacation_accrual_rate = vacation_accrual_rate)
        employee.save()
        return HttpResponse("Successfully created entry for %s." % employee_name) 
    raise Http404("Error, request wasn't POST")

@csrf_exempt
def addJob(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        try:
            job_id = json_data['job_id']
            job_title = json_data['job_title']
            employee_id = json_data['employee_id']
            employer_id = json_data['employer_id']
            employer_password = json_data['employer_key']
        except KeyError:
            raise Http404("JobID, EmployeeID, or employer info not found")
        if not checkEmployer(employer_id, employer_password) :
            raise Http404("Invalid Employer ID/Key")
        try:
            base_rate = json_data['base_rate']
        except KeyError:
            base_rate = 0
        try:
            incremental_rate_1 = json_data['incremental_rate_1']
        except KeyError:
            incremental_rate_1 = 0
        try:
            incremental_rate_2 = json_data['incremental_rate_2']
        except KeyError:
            incremental_rate_2 = 0
        job = Job(job_id=job_id, employee_id=employee_id, base_rate = base_rate, incremental_hours_1=incremental_hours_1, incremental_hours_2=incremental_hours_2, job_title = job_title)
        job.save()
        return HttpResponse("Successfully created entry for %s." % employee_id) 
    raise Http404("Error, request wasn't POST")

def parseTimecardData(json_entry):
    try:
        job_id = json_entry['job_id']
        employee_id = json_entry['employee_id']
        hours = json_entry['hours']
    except KeyError:
        raise Http404("Invalid time card entry")
    try:
        overtime_hours = json_entry['overtime_hours']
    except KeyError:
        overtime_hours = 0
    try:
        incremental_hours_1 = json_entry['incremental_hours_1']
    except KeyError:
        incremental_hours_1 = 0
    try:
        incremental_hours_2 = json_entry['incremental_hours_2']
    except KeyError:
        incremental_hours_2 = 0
    try:
        incremental_hours_1_and_2 = json_entry['incremental_hours_1_and_2']
    except KeyError:
        incremental_hours_1_and_2 = 0
    try:
        holiday_hours = json_entry['holiday_hours']
    except KeyError:
        holiday_hours = 0
    try:
        sick_hours = json_entry['sick_hours']
    except KeyError:
        sick_hours = 0
    try:
        vacation_hours = json_entry['vacation_hours']
    except KeyError:
        vacation_hours = 0
    try:
        holiday_hours_spent = json_entry['holiday_hours_spend']
    except KeyError:
        holiday_hours_spent = 0
    try:
        sick_hours_spent = json_entry['sick_hours_spent']
    except KeyError:
        sick_hours_spent = 0
    try:
        vacation_hours_spent = json_entry['vacation_hours_spent']
    except KeyError:
        vacation_hours_spent = 0
    return PayPeriod(employee_id=employee, job_id=job_id, hours = hours, overtime_hours = overtime_hours, incremental_hours_1 = incremental_hours_1, incremental_hours_2 = incremental_hours_2, incremental_hours_1_and_2 = incremental_hours_1_and_2, holiday_hours = holiday_hours, sick_hours = sick_hours, vacation_hours = vacation_hours, holiday_hours_spent = holiday_hours_spent, sick_hours_spent = sick_hours_spent, vacation_hours_spent = vacation_hours_spent)

@csrf_exempt
def addTimecardData(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        try:
            pay_period = json_data['pay_period']
            employer_id = json_data['employer_id']
            employer_password = json_data['employer_key']
        except KeyError:
            raise Http404("Pay period or employer info not found")
        if not checkEmployer(employer_id, employer_password) :
            raise Http404("Invalid Employer ID/Key")
        for json_entry in json_data['timecard_data']:
            entry = parseTimecardData(json_entry)
            entry.pay_start = entry.pay_period.start
            entry.pay_end = entry.pay_period.end
            entry.save();
        return HttpResponse("Successfully added %d timecards." % len(json_data)) 
    raise Http404("Error, request wasn't POST")
