from payroll_app.models import Employer, Employee, Job, BonusPay, PayPeriod, AuthUser
from django.contrib.auth.hashers import make_password
import auth_utils
import datetime

#Utility method to parse an employer from JSON data.
#does some ugly hard coding and stores the employer
def addCompanyJSON(json_data):
    try:
        employer_id = json_data['employer_id']
        if Employer.objects.filter(employer_id = employer_id).exists():
            raise Http404("Company Already Exists")
        employer_name = json_data['employer_name']
        employer_address = json_data['address']
        employer_key = json_data['key']
        employer_key = make_password(employer_key)
    except KeyError:
        raise Http404("Employer info not found")
    curDate = datetime.datetime.now()
    employer = Employer(employer_id=employer_id, employer_name=employer_name, address=employer_address, hash_key=employer_key, pay_start=curDate, pay_end=curDate)
    employer.save()
    return employer_name

#Utility method to parse an employee from JSON data.
#does some ugly hard coding and stores the employee
def addEmployeeJSON(json_data):
    try:
        employer_id = json_data['employer_id']
        employee_id = json_data['employee_id']
        if Employee.objects.filter(employee_id = employee_id).exists():
            raise Http404("Employee %s Already Exists" % employee_id)
        employer_key = json_data['employer_key']
    except KeyError:
        raise Http404("EmployeeID, or employer info not found")
    if not auth_utils.check_employer(employer_id, employer_key):
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
    return employee_name

#Utility method to parse a job from JSON data.
#does some ugly hard coding and stores the job
def addJobJSON(json_data):
    try:
        job_id = json_data['job_id']
        if Job.objects.filter(job_id = job_id).exists():
            raise Http404("Job %s Already Exists" % employee_id)
        job_title = json_data['job_title']
        employee_id = json_data['employee_id']
        employer_id = json_data['employer_id']
        employer_key = json_data['employer_key']
    except KeyError:
        raise Http404("JobID, EmployeeID, or employer info not found")
    if not auth_utils.check_employer(employer_id, employer_key) :
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
    job = Job(job_id=job_id, employee_id=employee_id, base_rate = base_rate, incremental_hours_1=incremental_rate_1, incremental_hours_2=incremental_rate_2, job_title = job_title)
    job.save()
    return job_title

#Utility method to parse a bulk timecard data from JSON data.
#does some ugly hard coding and stores the pay period
def addTimecardDataJSON(json_data):
    try:
        pay_period = json_data['pay_period']
        employer_id = json_data['employer_id']
        employer_key = json_data['employer_key']
        timecard_entries = json_data['timecard_data']
    except KeyError:
        raise Http404("Pay period or employer info not found")
    if not auth_utils.check_employer(employer_id, employer_key) :
        raise Http404("Invalid Employer ID/Key")
    for json_entry in timecard_entries:
        entry = parseTimecardData(json_entry)
        entry.pay_start = datetime.datetime.strptime(pay_period["start"], "%m/%d/%y")
        entry.pay_end = datetime.datetime.strptime(pay_period["end"], "%m/%d/%y")
        entry.save();
    return len(timecard_entries)

#Utility method to parse a bonus from JSON data.
#does some ugly hard coding and stores the bonus
def addBonusJSON(json_data):
    cur_time = datetime.datetime.now()
    try:
        bonus_id = json_data['bonus_id']
        employer_id = json_data['employer_id']
        employer_key = json_data['employer_key']
        employee_id = json_data['employee_id']
        amount = json_data['bonus_amount']
    except KeyError:
        raise Http404("Bonus, employee, or employer info not found")
    if not auth_utils.check_employer(employer_id, employer_key) :
        raise Http404("Invalid Employer ID/Key")
    try:
        pay_start = datetime.datetime.strptime(json_data["pay_start"], "%m/%d/%y")
    except KeyError:
        pay_start = cur_time
    try:
        pay_end = datetime.datetime.strptime(json_data["pay_end"], "%m/%d/%y")
    except KeyError:
        pay_end = cur_time
    try:
        date_given = datetime.datetime.strptime(json_data["data_given"], "%m/%d/%y")
    except KeyError:
        date_given = cur_time
    bonus = BonusPay(bonus_id=bonus_id, employee_id=employee_id, amount=amount, pay_start=pay_start, pay_end=pay_end, date_given=date_given)
    bonus.save()
    return employee_id

#Parses out the timecard data for a dictionary, doing
#error checking and validation
def parseTimecardData(json_entry):
    try:
        job_id = json_entry['job_id']
        employee_id = json_entry['employee_id']
        hours = json_entry['hours']
        employee = Employee.objects.get(employee_id = employee_id)
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
        employee.holiday_hours += int(holiday_hours)
    except KeyError:
        holiday_hours = 0
    try:
        sick_hours = json_entry['sick_hours']
        employee.sick_hours += int(sick_hours)
    except KeyError:
        sick_hours = 0
    try:
        vacation_hours = json_entry['vacation_hours']
        employee.vacation_hours += int(vacation_hours)
    except KeyError:
        vacation_hours = 0
    try:
        holiday_hours_spent = json_entry['holiday_hours_spent']
        employee.holiday_hours -= int(holiday_hours_spent)
    except KeyError:
        holiday_hours_spent = 0
    try:
        sick_hours_spent = json_entry['sick_hours_spent']
        employee.sick_hours -= int(sick_hours_spent)
    except KeyError:
        sick_hours_spent = 0
    try:
        vacation_hours_spent = json_entry['vacation_hours_spent']
        employee.vacation_hours -= int(vacation_hours_spent)
    except KeyError:
        vacation_hours_spent = 0
    employee.save()
    return PayPeriod(employee_id=employee_id, job_id=job_id, hours = hours, overtime_hours = overtime_hours, incremental_hours_1 = incremental_hours_1, incremental_hours_2 = incremental_hours_2, incremental_hours_1_and_2 = incremental_hours_1_and_2, holiday_hours = holiday_hours, sick_hours = sick_hours, vacation_hours = vacation_hours, holiday_hours_spent = holiday_hours_spent, sick_hours_spent = sick_hours_spent, vacation_hours_spent = vacation_hours_spent)
