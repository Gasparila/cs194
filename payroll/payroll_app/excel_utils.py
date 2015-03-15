from payroll_app.models import Employer, Employee, Job, BonusPay, PayPeriod, AuthUser
from django.contrib.auth.hashers import make_password
from xlrd import open_workbook
import auth_utils
import datetime

def add_timecard_data(employer_id, pay_start, pay_end, f):
    data_list = []
    days_in_period = 0
    wb = open_workbook(file_contents=f.read())
    for s in wb.sheets():
        for col in range(1, s.ncols, 2):
            
            obj = {}
            obj['hours'] = 0
            obj['pay_start'] = pay_start
            obj['pay_end'] = pay_end
            obj['hours'] = 0
            obj['holiday_hours'] = 0
            obj['vacation_hours'] = 0
            obj['sick_hours'] = 0
            obj['overtime_hours'] = 0
            obj['holiday_hours_spent'] = 0
            obj['sick_hours_spent'] = 0
            obj['vacation_hours_spent'] = 0
            obj['incremental_hours_1'] = 0
            obj['incremental_hours_2'] = 0
            obj['incremental_hours_1_and_2'] = 0
            job_id = s.cell(0, col).value
            if (isinstance(job_id, float) and int(job_id) == job_id): job_id = int(job_id)
            if (job_id == ""): return "No job id for employee number %d" % col/2 + 1
            obj['job_id'] = job_id
            if not Job.objects.filter(job_id = job_id).exists():
                return "There is no job with id %s" % job_id
            obj['employee_id'] = Job.objects.get(job_id=job_id).employee_id
            employee = Employee.objects.get(employee_id = obj['employee_id'])
            weekly_hours = 0
            for row in range(1, s.nrows):
                if (row) % 7 == 0:
                    weekly_hours = 0
                if (s.cell(row, col).value != "" and (col + 1 == s.ncols or s.cell(row, col + 1).value == "")):
                    overtime_hours = calculate_overtime(s.cell(row, col).value, weekly_hours)
                    obj['hours'] += s.cell(row, col).value - overtime_hours
                    obj['overtime_hours'] += overtime_hours
                elif (s.cell(row, col + 1).value.lower() == "vacation"):
                    obj['vacation_hours_spent'] += int(s.cell(row, col).value)
                    employee.vacation_hours -= int(s.cell(row, col).value)
                elif (s.cell(row, col + 1).value.lower() == "holiday"):
                    obj['holiday_hours_spent'] += int(s.cell(row, col).value)
                    employee.holiday_hours -= int(s.cell(row, col).value)
                elif (s.cell(row, col + 1).value.lower() == "sick"):
                    obj['sick_hours_spent'] += int(s.cell(row, col).value)
                    employee.sick_hours -= int(s.cell(row, col).value)
                elif (s.cell(row, col + 1).value.lower() == "incremental"):
                    obj['incremental_hours_1'] += int(s.cell(row, col).value)
                elif (s.cell(row, col + 1).value.lower() == "incremental2"):
                    obj['incremental_hours_2'] += int(s.cell(row, col).value)
            data_list.append(obj)
            employee.save()
    #This line of code translates each value in the data list into a PayPeriod object and enqueues it
    PayPeriod.objects.bulk_create(PayPeriod(**vals) for vals in data_list)
    return None

def calculate_overtime(daily_hours, weekly_hours):
    overtime_hours = 0
    if daily_hours > 8:
        overtime_hours = daily_hours - 8
    weekly_hours += daily_hours - overtime_hours
    if weekly_hours > 40:
        overtime_hours += weekly_hours - 40
        weekly_hours = 40
    return overtime_hours
