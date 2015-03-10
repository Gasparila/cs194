from payroll_app.models import Employer, Employee, Job, BonusPay, PayPeriod, AuthUser
import auth_utils

def addEmployee(employer_id, employer_key, employee_id, employee_name, address, vacation_hours=None, vacation_pay_rate=None, sick_hours=None, sick_pay_rate=None, vacation_accrual_rate=None):     
    if employer_id is None: return "Employer ID is required"
    if employee_id is None: return "Employee ID is required"
    if employee_name is None: return "Employee name is required"
    if address is None: return "Address is required"
    if Employee.objects.filter(employee_id = employee_id).exists():
        return "Employee with ID %s already exists" % employee_id
    if not auth_utils.check_employer(employer_id, employer_key):
        return "Invalid employer ID/key"
    if vacation_hours is None: vacation_hours = 0
    if sick_hours is None: sick_hours = 0
    if vacation_pay_rate is None: vacation_pay_rate = 0
    if sick_pay_rate is None: sick_pay_rate = 0
    if vacation_accrual_rate is None: vacation_accrual_rate = 0
    employee = Employee(employer_id=employer_id, employee_id=employee_id, employee_name=employee_name, address=address, vacation_hours = vacation_hours, vacation_pay_rate = vacation_pay_rate,  sick_hours = sick_hours, sick_pay_rate = sick_pay_rate, vacation_accrual_rate = vacation_accrual_rate)
    employee.save()
    return None
