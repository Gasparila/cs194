from payroll_app.models import Employer, Employee, Job, BonusPay, PayPeriod, AuthUser
import auth_utils
import datetime

def addEmployee(employer_id, employee_id, employee_name, address, vacation_hours=None, vacation_pay_rate=None, sick_hours=None, sick_pay_rate=None, vacation_accrual_rate=None):     
    if employer_id is None: return "Employer ID is required"
    if employee_id is None: return "Employee ID is required"
    if employee_name is None: return "Employee name is required"
    if address is None: return "Address is required"
    if Employee.objects.filter(employee_id = employee_id).exists():
        return "Employee with ID %s already exists" % employee_id
    if vacation_hours is None: vacation_hours = 0
    if sick_hours is None: sick_hours = 0
    if vacation_pay_rate is None: vacation_pay_rate = 0
    if sick_pay_rate is None: sick_pay_rate = 0
    if vacation_accrual_rate is None: vacation_accrual_rate = 0
    employee = Employee(employer_id=employer_id, employee_id=employee_id, employee_name=employee_name, address=address, vacation_hours = vacation_hours, vacation_pay_rate = vacation_pay_rate,  sick_hours = sick_hours, sick_pay_rate = sick_pay_rate, vacation_accrual_rate = vacation_accrual_rate)
    employee.save()
    return None

def addJob(employer_id, job_id, employee_id, job_title, base_rate=None, incremental_hours_1=None, incremental_hours_2=None):
    if employer_id is None: return "Employer ID is required"
    if job_id is None: return "Job ID is required"
    if employee_id is None: return "Employee ID is required"
    if job_title is None: return "Job title is required"
    try:
        base_rate = float(base_rate)
    except:
        base_rate = 0
    try:
        incremental_hours_1 = float(incremental_hours_1)
    except:
        incremental_hours_1 = 0
    try:
        incremental_hours_2 = float(incremental_hours_2)
    except:
        incremental_hours_2 = 0
    if Job.objects.filter(job_id = job_id).exists():
        return "Job %s Already Exists" % job_id
    job = Job(job_id=job_id, employee_id=employee_id, base_rate = base_rate, incremental_hours_1=incremental_hours_1, incremental_hours_2=incremental_hours_2, job_title = job_title)
    job.save()
    return None

def addBonus(employer_id, bonus_id, employee_id, amount, pay_start=None, pay_end=None, date_given=None):
    cur_time = datetime.datetime.now()
    if bonus_id is None: return "Bonus ID is required"
    if employee_id is None: return "Employee ID is required"
    if amount is None: return "Amount is required"
    try:
        pay_start = datetime.datetime.strptime(pay_start, "%m/%d/%y")
    except:
        pay_start = cur_time      
    try: 
        pay_end = datetime.datetime.strptime(pay_end, "%m/%d/%y")
    except:    
        pay_end = cur_time    
    try:        
        date_given = datetime.datetime.strptime(date_given, "%m/%d/%y")
    except:
        date_given = cur_time
    if BonusPay.objects.filter(bonus_id = bonus_id).exists():
        return "Bonus %s Already Exists" % bonus_id
    bonus = BonusPay(bonus_id=bonus_id, employee_id=employee_id, amount=amount, pay_start=pay_start, pay_end=pay_end, date_given=date_given)
    bonus.save()
    return None

def addEmployer(employer_id, employer_name, address, hash_key):
    #consider deleting the following
    cur_time = datetime.datetime.now()
    pay_start = cur_time
    pay_end = cur_time
    #end of portion to delete 
    if employer_id is None: return "Employer ID is required"
    if employer_name is None: return "Employer name is required"
    if address is None: return "Address is required"
    if hash_key is None: return "Hash key is required"
    if Employer.objects.filter(employer_id = employer_id).exists():
        return "Account with email %s already exists" % employer_id
    employer = Employer(employer_id=employer_id, employer_name=employer_name, address=address, pay_start=pay_start, pay_end=pay_end, hash_key=hash_key)
    employer.save()
    return None

