from payroll_app.models import Employer, Employee, Job, BonusPay, PayPeriod, AuthUser
from django.contrib.auth.hashers import make_password
import auth_utils
import datetime

#Utility method to parse one or more employees
#from a csv file.
def parse_employee_csv(csv_file):
    data_list = []
    metadata = {}
    lines = csv_file.splitlines()
    first = True
    for line in lines:
        obj = {}
        values = line.split(',')
        if first: #first line has metadata about employer
            first = False
            if (values[0] != ""):
                metadata['employer_id'] = values[0]
            if (values[1] != ""):
                metadata['employer_key'] = values[1]
            continue
        obj = copy.deepcopy(metadata)
        if (values[0] != ""):
            obj['employee_id'] = values[0]
        if (values[1] != ""):
            obj['employee_name'] = values[1]
        if (values[2] != ""):
            obj['employee_address'] = values[2]
        if (values[3] != ""):
            obj['vacation_hours'] = values[3]
        if (values[4] != ""):
            obj['sick_hours'] = values[4]
        if (values[5] != ""):
            obj['vacation_pay_rate'] = values[5]
        if (values[6] != ""):
            obj['sick_pay_rate'] = values[6]
        if (values[7] != ""):
            obj['vacation_accrual_rate'] = values[7]
        data_list.append(obj)
    return data_list

#Utility method to parse one or more jobs
#from a csv file.
def parse_job_csv(csv_file):
    data_list = []
    lines = csv_file.splitlines()
    first = True
    metadata = {}
    for line in lines:
        obj = {}
        values = line.split(',')
        if first: #first line has metadata about employer
            first = False
            if (values[0] != ""):
                metadata['employer_id'] = values[0]
            if (values[1] != ""):
                metadata['employer_key'] = values[1]
            continue
        obj = copy.deepcopy(metadata)
        if (values[0] != ""):
            obj['job_id'] = values[0]
        if (values[1] != ""):
            obj['job_title'] = values[1]
        if (values[2] != ""):
            obj['employee_id'] = values[2]
        if (values[3] != ""):
            obj['base_rate'] = values[3]
        if (values[4] != ""):
            obj['incremental_rate_1'] = values[4]
        if (values[5] != ""):
            obj['incremental_rate_2'] = values[5]
        data_list.append(obj)
    return data_list

#Utility method to parse one or more time cards
#from a csv file.
def parse_timecard_csv(csv_file):
    data = {}
    data_list = []
    lines = csv_file.splitlines()
    first = True
    for line in lines:
        obj = {}
        values = line.split(',')
        if first: #first line has metadata about employer and pay period
            first = False
            if (values[0] != "" and values[1] != ""):
                pay_period_start = values[0] 
                pay_period_end = values[1]
                data["pay_period"] = {"start":pay_period_start, "end":pay_period_end}
            if (values[2] != ""):
                data["employer_id"] = values[2]
            if (values[3] != ""):
                data["employer_key"] = values[3]
            continue
        if (values[0] != ""):
            obj['job_id'] = values[0]
        if (values[1] != ""):
            obj['employee_id'] = values[1]
        if (values[2] != ""):
            obj['hours'] = values[2]
        if (values[3] != ""):
            obj['overtime_hours'] = values[3]
        if (values[4] != ""):
            obj['holiday_hours_spent'] = values[4]
        if (values[5] != ""):
            obj['sick_hours_spent'] = values[5]
        if (values[6] != ""):
            obj['vacation_hours_spent'] = values[6]
        if (values[7] != ""):
            obj['incremental_hours_1'] = values[7]
        if (values[8] != ""):
            obj['incremental_hours_2'] = values[8]
        if (values[9] != ""):
            obj['incremental_hours_1_and_2'] = values[9]
        if (values[10] != ""):
            obj['holiday_hours'] = values[10]
        if (values[11] != ""):
            obj['sick_hours'] = values[11]
        if (values[12] != ""):
            obj['vacation_hours'] = values[12]
        data_list.append(obj)
    data['timecard_data'] = data_list
    return data

#Utility method to parse one or more daily
#time cards from a csv file.
def add_daily_timecard_data_csv(csv_file):
    data = {}
    data_list = []
    lines = csv_file.splitlines()
    first = True
    days_in_period = 0
    for line in lines:
        obj = {}
        values = line.split(',')
        if first: #first line has metadata about employer and pay period
            first = False
            if (values[0] != "" and values[1] != ""):
                pay_period_start = values[0] 
                pay_period_end = values[1]
                data["pay_period"] = {"start":pay_period_start, "end":pay_period_end}
            if (values[2] != ""):
                data["employer_id"] = values[2]
            if (values[3] != ""):
                data["employer_key"] = values[3]
            if (values[4] != ""):
                days_in_period = int(values[4])
            continue
        obj['hours'] = 0
        obj['overtime_hours'] = 0
        obj['holiday_hours_spent'] = 0
        obj['sick_hours_spent'] = 0
        obj['vacation_hours_spent'] = 0
        obj['incremental_hours_1'] = 0
        obj['incremental_hours_2'] = 0
        obj['incremental_hours_1_and_2'] = 0
        if (values[0] != ""):
            obj['job_id'] = values[0]
        if (values[1] != ""):
            obj['employee_id'] = values[1]
        weekly_hours = 0
        for i in range(2, len(values), 2):
            if (i/2) % 7 == 0:
                weekly_hours = 0
            if (values[i] != "" and values[i + 1] == ""):
                overtime_hours = calculate_overtime(values[i], weekly_hours)
                obj['hours'] += values[i] - overtime_hours
                obj['overtime_hours'] += overtime_hours
            if (values[i + 1].lower() == "vacation"):
                obj['vacation_hours_spent'] += int(values[i + 1])
            if (values[i + 1].lower() == "holiday"):
                obj['holiday_hours_spent'] += int(values[i + 1])
            if (values[i + 1].lower() == "sick"):
                obj['sick_hours_spent'] += int(values[i + 1])
            if (values[i + 1].lower() == "incremental"):
                obj['incremental_hours_1'] += int(values[i + 1])
            if (values[i + 1].lower() == "incremental2"):
                obj['incremental_hours_2'] += int(values[i + 1])
        data_list.append(obj)
    data['timecard_data'] = data_list
    return data

#calculates the overtime. In California, overtime is
#earned by working more than 8 hours in a given day,
# or more than 40 non-overtime hours in a week
def calculate_overtime(daily_hours, weekly_hours):
    overtime_hours = 0
    if daily_hours > 8:
        overtime_hours = daily_hours - 8
    weekly_hours += daily_hours - overtime_hours
    if weekly_hours > 40:
        overtime_hours += weekly_hours - 40
        weekly_hours = 40
    return over_time

#Utility method for adding one or more bonuses
#from a csv file
def parse_bonus_csv(csv_file):
    metadata = {}
    data_list = []
    lines = csv_file.splitlines()
    first = True
    for line in lines:
        obj = {}
        values = line.split(',')
        if first:
            first = False
            if (values[0] != ""):
                metadata['employer_id'] = values[0]
            if (values[1] != ""):
                metadata['employer_key'] = values[1]
            if (values[2] != ""):
                metadata["pay_start"] = values[2]
            if (values[3] != ""):
                metadata["pay_end"] = values[3]
            if (values[4] != ""):
                metadata["data_given"] = values[4]
            continue
        obj = copy.deepcopy(metadata)
        if (values[0] != ""):
            obj['bonus_id'] = values[0]
        if (values[1] != ""):
            obj['employee_id'] = values[1]
        if (values[2] != ""):
            obj['bonus_amount'] = values[2]
        data_list.append(obj)
    return data_list
