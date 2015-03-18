from payroll_app.models import Employer, Employee, Job, BonusPay, PayPeriod, AuthUser
import auth_utils
import datetime
import excel_utils

#Adds an employee with data received from a HTTP POST request. Validation is performed
def addEmployee(employer_id, employee_id, employee_name, address, vacation_hours=None, vacation_pay_rate=None, sick_hours=None, sick_pay_rate=None, vacation_accrual_rate=None):     
    if (employer_id or '') == '': return "Employer ID is required"
    if (employee_id or '') == '': return "Employee ID is required"
    if (employee_name or '') == '': return "Employee name is required"
    if (address or '') == '': return "Address is required"
    if Employee.objects.filter(employee_id = employee_id).exists():
        return "Employee with ID %s already exists" % employee_id
    if (vacation_hours or '') == '': vacation_hours = 0
    if (sick_hours or '') == '': sick_hours = 0
    if (vacation_pay_rate or '') == '': vacation_pay_rate = 0
    if (sick_pay_rate or '') == '': sick_pay_rate = 0
    if (vacation_accrual_rate or '') == '': vacation_accrual_rate = 0
    employee_name = employee_name.strip()
    address = address.strip()
    employee = Employee(employer_id=employer_id, employee_id=employee_id, employee_name=employee_name, address=address, vacation_hours = vacation_hours, vacation_pay_rate = vacation_pay_rate,  sick_hours = sick_hours, sick_pay_rate = sick_pay_rate, vacation_accrual_rate = vacation_accrual_rate)
    employee.save()
    return None

#Adds a job with data received from a HTTP POST request. Validation is performed
def addJob(employer_id, job_id, employee_id, job_title, base_rate=None, incremental_hours_1=None, incremental_hours_2=None):
    if (employer_id or '') == '': return "Employer ID is required"
    if (job_id or '') == '': return "Job ID is required"
    if (employee_id or '') == '': return "Employee ID is required"
    if (job_title or '') == '': return "Job title is required"
    if (base_rate or '') == '': return "Base Rate is required"
    if not Employee.objects.filter(employee_id = employee_id).exists():
        return "There is no employee with id %s" % employee_id
    try:
        if base_rate[0] == '$':
            base_rate = base_rate[1:]
        base_rate = float(base_rate)
    except:
        return "Improper formatted base rate"
    try:
        incremental_hours_1 = float(incremental_hours_1)
    except:
        if incremental_hours_1  and incremental_hours_1  != '':
            return "improper formatted incremental hours 1"
        incremental_hours_1 = 0
    try:
        incremental_hours_2 = float(incremental_hours_2)
    except:
        if incremental_hours_2  and incremental_hours_2  != '':
            return "improper formatted incremental hours 2"
        incremental_hours_2 = 0
    if Job.objects.filter(job_id = job_id).exists():
        return "Job %s Already Exists" % job_id
    job_title = job_title.strip()
    job = Job(job_id=job_id, employee_id=employee_id, base_rate = base_rate, incremental_hours_1=incremental_hours_1, incremental_hours_2=incremental_hours_2, job_title = job_title)
    job.save()
    return None

#Adds a bonus with data received from a HTTP POST request. Validation is performed
def addBonus(employer_id, bonus_id, employee_id, amount, pay_start=None, pay_end=None, date_given=None):
    cur_time = datetime.datetime.now()
    if (bonus_id or '') == '': return "Bonus ID is required"
    if (employee_id or '') == '': return "Employee ID is required"
    if (amount or '') == '': return "Amount is required"
    try:
        if amount[0] == '$':
            amount = base_rate[1:]
        fl = float(amount) #Hack: Make sure it is a valid number
    except:
        return "Improper format of amount"
    if not Employee.objects.filter(employee_id = employee_id).exists():
        return "There is no employee with id %s" % employee_id
    try:
        pay_start = datetime.datetime.strptime(pay_start, "%Y-%m-%d")
    except:
        pay_start = cur_time      
    try: 
        pay_end = datetime.datetime.strptime(pay_end, "%Y-%m-%d")
    except:    
        pay_end = cur_time    
    try:        
        date_given = datetime.datetime.strptime(date_given, "%Y-%m-%d")
    except:
        date_given = cur_time
    if BonusPay.objects.filter(bonus_id = bonus_id).exists():
        return "Bonus %s Already Exists" % bonus_id
    bonus = BonusPay(bonus_id=bonus_id, employee_id=employee_id, amount=amount, pay_start=pay_start, pay_end=pay_end, date_given=date_given)
    bonus.save()
    return None

#Adds a pay period with data received from a HTTP POST request. Validation is performed
def addPayPeriod(employer_id, pay_start, pay_end, timecard_data):
    if (employer_id or '') == '': return "Employer ID is required"
    if (pay_start or '') == '': return "Pay Start is required"
    if (pay_end or '') == '': return "Pay End is required"
    if (timecard_data or '') == '': return "Timecard Data is required"
    try:
        pay_start = datetime.datetime.strptime(pay_start, "%Y-%m-%d")
    except:
        return "Invalid start date"
    try: 
        pay_end = datetime.datetime.strptime(pay_end, "%Y-%m-%d")
    except:    
        return "Invalid end date"
    return excel_utils.add_timecard_data(employer_id, pay_start, pay_end, timecard_data)

#Adds an employer with data received from a HTTP POST request. Validation is performed
def addEmployer(employer_id, employer_name, address, hash_key):
    #consider deleting the following
    cur_time = datetime.datetime.now()
    pay_start = cur_time
    pay_end = cur_time
    #end of portion to delete 
    if (employer_id or '') == '': return "Employer ID is required"
    if (employer_name or '') == '': return "Employer name is required"
    if (address or '') == '': return "Address is required"
    if (hash_key or '') == '': return "Hash key is required"
    if Employer.objects.filter(employer_id = employer_id).exists():
        return "Account with email %s already exists" % employer_id
    employer_name = employer_name.strip()
    employer = Employer(employer_id=employer_id, employer_name=employer_name, address=address, pay_start=pay_start, pay_end=pay_end, hash_key=hash_key)
    employer.save()
    return None

