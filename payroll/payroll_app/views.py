from django.db import models
from django.contrib import auth, messages
from django.contrib.messages import get_messages
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from decimal import *
from tempfile import *
from payroll_app.models import Employer, Employee, Job, BonusPay, PayPeriod, AuthUser
from subprocess import Popen, PIPE
from subprocess import call
import copy
import datetime
import json
import reportlab
import JSON_utils
import auth_utils
import csv_utils

def employeeCSVBuilder( start_time, end_time, employee_id, employer_id):
    employer = Employer.objects.get(employer_id = employer_id)
    tex_file = ""
    payperiod1 = PayPeriod.objects.all().filter(employee_id=employee_id)
    payperiod1 = payperiod1.filter(pay_start__gte = start_time)
    payperiod1 = payperiod1.filter(pay_end__lte = end_time)
    employee = Employee.objects.all().get(employee_id = employee_id)
    jobs = Job.objects.all().filter(employee_id = employee_id)
    employee_info = "To:, " + employee.employee_name + "\nAddress:, " + employee.address + "\n\n"  
    tex_file += employee_info;
    employer_info = "From: " + employer.employer_name + "\nAddress:, " + employer.address + "\n\n"  
    tex_file += employer_info
    for payperiod in payperiod1:
        for job in jobs:
            if job.job_id == payperiod.job_id:
                payPeriod_info = "Pay Period:, " + str(payperiod.pay_start.strftime('%b %d, %Y')) + ", to, " + str(payperiod.pay_end.strftime('%b %d, %Y')) + " \nJob:, " + job.job_title + " \n"
                tex_file += payPeriod_info
                table_start = "Type, Hours, Rate, Payment\n"      
                tex_file += table_start
                base_pay =  payperiod.hours * job.base_rate;
                base_row = "Base," + str(payperiod.hours) + ", " + str(job.base_rate) + ", " + str(base_pay) + " \n"   
                tex_file += base_row 
                total = base_pay;
                if payperiod.overtime_hours > 0: 
                    overtime_pay =  payperiod.overtime_hours * (Decimal(job.base_rate) * Decimal(1.5));
                    total = total + overtime_pay
                    overtime_row = "Overtime, " + str(payperiod.overtime_hours) + ", " + str((job.base_rate * Decimal(1.5))) + ", " + str(overtime_pay) + "\n"   
                    tex_file +=overtime_row; 
                if payperiod.incremental_hours_1 > 0:
                    incremental_pay1 =  payperiod.incremental_hours_1 * (job.base_rate + job.incremental_hours_1);
                    total = total + incremental_pay1
                    incremental_row1 = "Incremental 1, " + str(payperiod.incremental_hours_1) + ", " + str((job.base_rate + job.incremental_hours_1)) + ", " + str(incremental_pay1) + "\n"   
                    tex_file +=incremental_row1; 
                if payperiod.incremental_hours_2 > 0:
                    incremental_pay2 =  payperiod.incremental_hours_2 * (job.base_rate + job.incremental_hours_2);
                    incremental_row2 = "Incremental 2, " + str(payperiod.incremental_hours_2) + ", " + str((job.base_rate + job.incremental_hours_2)) + ", " + str(incremental_pay2) + "\n"   
                    total = total + incremental_pay2
                    tex_file +=incremental_row2;
                if payperiod.incremental_hours_1_and_2 > 0:
                    incremental_pay12 =  payperiod.incremental_hours_1_and_2 * (job.base_rate + job.incremental_hours_2 + job.incremental_hours_1);
                    incremental_row12 = "Incremental 1 and 2, " + str(payperiod.incremental_hours_1_and_2) + ", " + str((job.base_rate + job.incremental_hours_2 + job.incremental_hours_1)) + ", " + str(incremental_pay12) + "\n"   
                    total = total + incremental_pay12
                    tex_file += incremental_row12;
                if payperiod.vacation_hours_spent > 0:
                    vacation_rate = employee.vacation_pay_rate
                    if vacation_rate == 0: 
                        vacation_rate = job.base_rate
                    vacation_pay =  payperiod.vacation_hours_spent * (vacation_rate);
                    total = total + vacation_pay
                    vacation_row = "Vacation, " + str(payperiod.vacation_hours_spent) + ", " + str((vacation_rate)) + ", " + str(vacation_pay) + "\n"   
                    tex_file += vacation_row; 
                if payperiod.sick_hours_spent > 0:
                    sick_rate = employee.sick_pay_rate;
                    if sick_rate == 0: 
                        sick_rate = job.base_rate
                    sick_pay =  payperiod.sick_hours_spent * (sick_rate);
                    total = total + sick_pay
                    sick_row = "Sick, " + str(payperiod.sick_hours_spent) + ", " + str((sick_rate)) + ", " + str(sick_pay) + "\n"   
                    tex_file += sick_row;
                if payperiod.holiday_hours_spent > 0:
                    holiday_pay_rate = employee.vacation_pay_rate;
                    if holiday_pay_rate  == 0: 
                        holiday_pay_rate  = job.base_rate
                    holiday_pay =  payperiod.holiday_hours_spent * (holiday_pay_rate);
                    total = total + holiday_pay                        
                    holiday_row = "Holiday, " + str(payperiod.holiday_hours_spent) + ", " + str((holiday_pay_rate)) + ", " + str(holiday_pay) + "\n"   
                    tex_file +=holiday_row;
                total_row = "Total,,," + str(total) + "\n\n\n";
                tex_file +=total_row;
                table_start = "Type, Hours Gained, Total\n"
                tex_file += table_start;
                vacation_row = "Vacation Hours, " + str(payperiod.vacation_hours) + ", " + str((employee.vacation_hours)) +" \n" 
                sick_row = "Sick Hours, " + str(payperiod.sick_hours) + ", " + str((employee.sick_hours)) +"\n" 
                tex_file += vacation_row
                tex_file += sick_row
    return tex_file

def employeeBuilder( start_time, end_time, employee_id, employer_id):
    employer = Employer.objects.get(employer_id = employer_id)
    tex_file = "\\documentclass[14pt]{article}\n\\newcommand{\\tab}[1]{\\hspace{.2\\textwidth}\\rlap{1}}\n\\begin{document}\n\\setlength{\\parindent}{0pt}\n\n"
    payperiod1 = PayPeriod.objects.all().filter(employee_id=employee_id)
    payperiod1 = payperiod1.filter(pay_start__gte = start_time)
    payperiod1 = payperiod1.filter(pay_end__lte = end_time)
    employee = Employee.objects.all().get(employee_id = employee_id)
    jobs = Job.objects.all().filter(employee_id = employee_id)
    employee_info = "To: " + employee.employee_name + "\\\\\nAddress: " + employee.address + "\\\\\n\n"  
    tex_file += employee_info;
    employer_info = "From: " + employer.employer_name + "\\\\\nAddress: " + employer.address + "\\\\\n\n"  
    tex_file += employer_info
    for payperiod in payperiod1:
        for job in jobs:
            if job.job_id == payperiod.job_id:
                payPeriod_info = "Pay Period: " + str(payperiod.pay_start.strftime('%b %d, %Y')) + " to " + str(payperiod.pay_end.strftime('%b %d, %Y')) + " \\\\\nJob: " + job.job_title + " \\\\\n\n"
                tex_file += payPeriod_info
                table_start = "\\begin{table}[htb]\n\\begin{tabular}{| l | l | l | l | }\n\\hline\n\\textbf{Type} & \\textbf{Hours} & \\textbf{Rate} & \\textbf{Payment} \\\\\n\\hline\n"      
                tex_file += table_start
                base_pay =  payperiod.hours * job.base_rate;
                base_row = "Base & " + str(payperiod.hours) + " & " + str(job.base_rate) + " & " + str(base_pay) + " \\\\\n\\hline\n"   
                tex_file += base_row 
                total = base_pay;
                if payperiod.overtime_hours > 0: 
                    overtime_pay =  payperiod.overtime_hours * (Decimal(job.base_rate) * Decimal(1.5));
                    total = total + overtime_pay
                    overtime_row = "Overtime & " + str(payperiod.overtime_hours) + " & " + str((job.base_rate * Decimal(1.5))) + " & " + str(overtime_pay) + " \\\\\n\\hline\n"   
                    tex_file +=overtime_row; 
                if payperiod.incremental_hours_1 > 0:
                    incremental_pay1 =  payperiod.incremental_hours_1 * (job.base_rate + job.incremental_hours_1);
                    total = total + incremental_pay1
                    incremental_row1 = "Incremental 1 & " + str(payperiod.incremental_hours_1) + " & " + str((job.base_rate + job.incremental_hours_1)) + " & " + str(incremental_pay1) + " \\\\\n\\hline\n"   
                    tex_file +=incremental_row1; 
                if payperiod.incremental_hours_2 > 0:
                    incremental_pay2 =  payperiod.incremental_hours_2 * (job.base_rate + job.incremental_hours_2);
                    incremental_row2 = "Incremental 2 & " + str(payperiod.incremental_hours_2) + " & " + str((job.base_rate + job.incremental_hours_2)) + " & " + str(incremental_pay2) + " \\\\\n\\hline\n"   
                    total = total + incremental_pay2
                    tex_file +=incremental_row2;
                if payperiod.incremental_hours_1_and_2 > 0:
                    incremental_pay12 =  payperiod.incremental_hours_1_and_2 * (job.base_rate + job.incremental_hours_2 + job.incremental_hours_1);
                    incremental_row12 = "Incremental 1 and 2 & " + str(payperiod.incremental_hours_1_and_2) + " & " + str((job.base_rate + job.incremental_hours_2 + job.incremental_hours_1)) + " & " + str(incremental_pay12) + " \\\\\n\\hline\n"   
                    total = total + incremental_pay12
                    tex_file += incremental_row12;
                if payperiod.vacation_hours_spent > 0:
                    vacation_rate = employee.vacation_pay_rate
                    if vacation_rate == 0: 
                        vacation_rate = job.base_rate
                    vacation_pay =  payperiod.vacation_hours_spent * (vacation_rate);
                    total = total + vacation_pay
                    vacation_row = "Vacation & " + str(payperiod.vacation_hours_spent) + " & " + str((vacation_rate)) + " & " + str(vacation_pay) + " \\\\\n\\hline\n"   
                    tex_file += vacation_row; 
                if payperiod.sick_hours_spent > 0:
                    sick_rate = employee.sick_pay_rate;
                    if sick_rate == 0: 
                        sick_rate = job.base_rate
                    sick_pay =  payperiod.sick_hours_spent * (sick_rate);
                    total = total + sick_pay
                    sick_row = "Sick & " + str(payperiod.sick_hours_spent) + " & " + str((sick_rate)) + " & " + str(sick_pay) + " \\\\\n\\hline\n"   
                    tex_file += sick_row;
                if payperiod.holiday_hours_spent > 0:
                    holiday_pay_rate = employee.vacation_pay_rate;
                    if holiday_pay_rate  == 0: 
                        holiday_pay_rate  = job.base_rate
                    holiday_pay =  payperiod.holiday_hours_spent * (holiday_pay_rate);
                    total = total + holiday_pay                        
                    holiday_row = "Holiday & " + str(payperiod.holiday_hours_spent) + " & " + str((holiday_pay_rate)) + " & " + str(holiday_pay) + " \\\\\n\\hline\n"   
                    tex_file +=holiday_row;
                total_row = "\\textbf{Total} & & & \\textbf{" + str(total) + "}\\\\\n\\hline\n\\end{tabular}\n\\end{table}\n\n\n";
                tex_file +=total_row;
                table_start = "\\begin{table}[htb]\n\\begin{tabular}{| l | l | l | }\n\\hline\n\\textbf{Type} & \\textbf{Hours Gained} & \\textbf{Total} \\\\\n\\hline\n"
                tex_file += table_start;
                vacation_row = "Vacation Hours & " + str(payperiod.vacation_hours) + " & " + str((employee.vacation_hours)) +" \\\\\n\\hline\n" 
                sick_row = "Sick Hours & " + str(payperiod.sick_hours) + " & " + str((employee.sick_hours)) +" \\\\\n\\hline\n" 
                tex_file += vacation_row
                tex_file += sick_row
                table_end = "\\end{tabular}\n\\end{table}\n\n\n"
                tex_file += table_end
    tex_file += "\\end{document}"
    return tex_file

def employeeSearch(request):
    if not request.user.is_authenticated(): return redirect('login/')   
    else:
        return render(request, 'employee_search.html', {})  

def employerBuilder(start_time, end_time, employer_id, columns, show_incremental_hours, show_overtime_hours, show_holiday_hours, show_vacation_hours, show_sick_hours, show_holiday_hours_spent, show_vacation_hours_spent, show_sick_hours_spent):
    employer = Employer.objects.get(employer_id = employer_id)
    tex_file = "\\documentclass[14pt]{article}\n\\newcommand{\\tab}[1]{\\hspace{.2\\textwidth}\\rlap{1}}\n\\begin{document}\n\\setlength{\\parindent}{0pt}\n\n"
    employees = Employee.objects.all().filter(employer_id = employer_id)
    employer_info = "To: " + employer.employer_name + "\\\\\nAddress: " + employer.address + "\\\\\n\n"  
    tex_file += employer_info
    table = "| l | l | l | l | l | l |"
    for i in range(columns):
        table += " l |"
    allTotal = 0;
    table_start = "\\begin{table}[htb]\n\\begin{tabular}{" + table + "}\n\\hline\n\\textbf{Employee} & \\textbf{Job} & \\textbf{Start Date} & \\textbf{End Date} & \\textbf{Hours} & \\textbf{Payment} \\\\\n\\hline\n"      
    tex_file +=table_start
    for employee in employees: 
        employee_id = employee.employee_id
        payperiod1 = PayPeriod.objects.all().filter(employee_id=employee_id)
        payperiod1 = payperiod1.filter(pay_start__gte = start_time)
        payperiod1 = payperiod1.filter(pay_end__lte = end_time)
        jobs = Job.objects.all().filter(employee_id = employee_id)
        for payperiod in payperiod1:
            for job in jobs:
                if job.job_id == payperiod.job_id:
                    all_row = employee.employee_name + " & " + job.job_title + " & " + str(payperiod.pay_start.strftime('%b %d, %Y')) + " & " + str(payperiod.pay_end.strftime('%b %d, %Y')) + " & "
                    total_hours = payperiod.sick_hours_spent + payperiod.holiday_hours_spent + payperiod.vacation_hours_spent + payperiod.hours + payperiod.overtime_hours +  payperiod.incremental_hours_1 + payperiod.incremental_hours_2 + payperiod.incremental_hours_1_and_2
                    base_pay =  payperiod.hours * job.base_rate;
                    total = base_pay;
                    if payperiod.overtime_hours > 0: 
                        overtime_pay =  payperiod.overtime_hours * (Decimal(job.base_rate) * Decimal(1.5));
                        total = total + overtime_pay
                    if payperiod.incremental_hours_1 > 0:
                        incremental_pay1 =  payperiod.incremental_hours_1 * (job.base_rate + job.incremental_hours_1);
                        total = total + incremental_pay1
                    if payperiod.incremental_hours_2 > 0:
                        incremental_pay2 =  payperiod.incremental_hours_2 * (job.base_rate + job.incremental_hours_2);
                        total = total + incremental_pay2;
                    if payperiod.incremental_hours_1_and_2 > 0:
                        incremental_pay12 =  payperiod.incremental_hours_1_and_2 * (job.base_rate + job.incremental_hours_2 + job.incremental_hours_1);
                        total = total + incremental_pay12;
                    if payperiod.vacation_hours_spent > 0:
                        vacation_rate = employee.vacation_pay_rate
                        if vacation_rate == 0: 
                            vacation_rate = job.base_rate
                        vacation_pay =  payperiod.vacation_hours_spent * (vacation_rate);
                        total = total + vacation_pay
                    if payperiod.sick_hours_spent > 0:
                        sick_rate = employee.sick_pay_rate;
                        if sick_rate == 0: 
                            sick_rate = job.base_rate
                        sick_pay =  payperiod.sick_hours_spent * (sick_rate);
                        total = total + sick_pay
                    if payperiod.holiday_hours_spent > 0:
                        holiday_pay_rate = employee.vacation_pay_rate;
                        if holiday_pay_rate  == 0: 
                            holiday_pay_rate  = job.base_rate
                        holiday_pay =  payperiod.holiday_hours_spent * (holiday_pay_rate);
                        total = total + holiday_pay   
                    allTotal += total;
                    all_row = all_row + "" + str(total_hours) + " & " + str(total) + "\\\\\n\\hline\n"    
                    tex_file += all_row;                
    tex_file += "\\textbf{Total:} & & & & & \\textbf{\\$" + str(allTotal) + "}\\\\\n\\hline\n"
    end_table = "\\hline\n\\end{tabular}\n\\end{table}\n\n\n";
    tex_file += end_table;
    tex_file += "\\end{document}"
    return tex_file
# Create your views here.
def index(request):
    #If the user is logged in, show them the dashboard
    if request.user.is_authenticated(): return render(request, 'index.html', {})
    #Try logging them in
    email = request.POST.get('email')
    password = request.POST.get('password')
    user = auth.authenticate(username=email, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return render(request, 'index.html', {})
        else:
            messages.add_message(request, messages.INFO, 'Inactive user account')
            return redirect('login/')           
    else:
        if email is not None and password is not None: 
            messages.add_message(request, messages.INFO, 'Invalid login information')
        return redirect('login/')   

def login(request):
    storage = get_messages(request)
    return render(request, 'login.html', {})

def logout(request):
    auth.logout(request)
    return redirect('/')            

def createAccounts(request):
    user = AuthUser.objects.create_user('naveenk1@stanford.edu', password='password')
    user.save()
    return redirect('login/')    

@csrf_exempt
def getPayrollCSV(request):

    #Employer.objects.all().delete()
    #Employee.objects.all().delete()
    #Job.objects.all().delete()
    #PayPeriod.objects.all().delete()
    #employer1 = Employer(employer_id="12468",employer_name="Amazon", address="265 Lytton Ave.", pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), hash_key=make_password("HASHVALUE1"))
    #employer2 = Employer(employer_id="13492",employer_name="Microsoft", address="610 Mayfield Ave", pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), hash_key=make_password("HASHVALUE2"))
    #employee1 = Employee(employee_id="78932",employer_id="12468", employee_name = "Naveen Krishnamurthi", vacation_hours = 6.00, vacation_pay_rate = 60.00, sick_hours = 12.00, sick_pay_rate = 60.00, vacation_accrual_rate = 0.01, address="12795 Calle De La Siena, San Diego CA, 92130")
    #employee2 = Employee(employee_id="78777",employer_id="13492", employee_name = "Danial Shakeri", vacation_hours = 8.00, vacation_pay_rate = 62.00, sick_hours = 13.00, sick_pay_rate = 64.00, vacation_accrual_rate = 0.02, address="265 Westfield Ave., San Diego CA, 92130")
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
    # PayPeriod.objects.all().delete()
    # payPeriod1 = PayPeriod(employee_id="78777", job_id="8935", pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), hours = 40, overtime_hours = 2, incremental_hours_1 = 1, incremental_hours_2 = 2, incremental_hours_1_and_2 = 2, holiday_hours = 10, sick_hours = 12, vacation_hours = 12, holiday_hours_spent = 4, sick_hours_spent = 2, vacation_hours_spent = 1)
    # payPeriod2 = PayPeriod(employee_id="78777", job_id="8935", pay_start=datetime.datetime(2013, 12, 1, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 10, 17, 18, 40), hours = 40, overtime_hours = 2, incremental_hours_1 = 1, incremental_hours_2 = 2, incremental_hours_1_and_2 = 2, holiday_hours = 10, sick_hours = 12, vacation_hours = 12, holiday_hours_spent = 4, sick_hours_spent = 2, vacation_hours_spent = 1)
    # payPeriod3 = PayPeriod(employee_id="78412", job_id="8936", pay_start=datetime.datetime(2013, 12, 1, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 10, 17, 18, 40), hours = 40, overtime_hours = 2, incremental_hours_1 = 1, incremental_hours_2 = 2, incremental_hours_1_and_2 = 2, holiday_hours = 10, sick_hours = 12, vacation_hours = 12, holiday_hours_spent = 4, sick_hours_spent = 2, vacation_hours_spent = 1)
    # payPeriod4 = PayPeriod(employee_id="78932", job_id="7412", pay_start=datetime.datetime(2013, 12, 1, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 10, 17, 18, 40), hours = 40, overtime_hours = 2, incremental_hours_1 = 1, incremental_hours_2 = 2, incremental_hours_1_and_2 = 2, holiday_hours = 10, sick_hours = 12, vacation_hours = 12, holiday_hours_spent = 4, sick_hours_spent = 2, vacation_hours_spent = 1)

    # payPeriod1.save()
    # payPeriod2.save()
    # payPeriod3.save()
    # payPeriod4.save()
    json_data = json.loads(request.body)

    try:
        employer_id = json_data['employer_id']
        employer_key = json_data['key']
        start = json_data['start']
        end = json_data['end']
    except KeyError:
        raise Http404("EmployeeID, or employer info not found")
    if not auth_utils.check_employer(employer_id, employer_key):
        raise Http404("Invalid Employer ID/Key" )
    try:
        employee_id = json_data['employee_id']
    except KeyError:
        raise Http404("Employee info not found")

    columns = 0;
    try:
        show_incremental_hours = json_data['incremental_hours']
        columns += 3;
        show_incremental_hours = True
    except KeyError:
        show_incremental_hours = False 
    try:
        show_overtime_hours = json_data['overtime_hours']
        show_overtime_hours = True
        columns+=1;
    except KeyError:
        show_overtime_hours = False 
    try:
        show_holiday_hours = json_data['holiday_hours']
        show_holiday_hours = True
        columns+=1;
    except KeyError:
        show_holiday_hours = False
    try:
        show_vacation_hours = json_data['vacation_hours']
        columns+=1;
        show_vacation_hours = True
    except KeyError:
        show_vacation_hours = False
    try:
        show_sick_hours = json_data['sick_hours']
        columns+=1;
        show_sick_hours = True
    except KeyError:
        show_sick_hours = False
    try:
        show_holiday_hours_spent = json_data['holiday_hours_spent']
        columns+=1;
        show_holiday_hours_spent = True
    except KeyError:
        show_holiday_hours_spent = False
    try:
        show_vacation_hours_spent = json_data['vacation_hours_spent']
        columns+=1;
        show_vacation_hours_spent = True
    except KeyError:
        show_vacation_hours_spent = False
    try:
        show_sick_hours_spent = json_data['sick_hours_spent']
        columns+=1;
        show_sick_hours_spent = True
    except KeyError:
        show_sick_hours_spent = False

    start_time = datetime.datetime.strptime(start, "%m/%d/%y")
    end_time = datetime.datetime.strptime(end, "%m/%d/%y")
    tex_name =  "./" + employer_id + "_" + employee_id + ".tex" 
    pdf_name = employer_id + "_" + employee_id + ".pdf"
    
    pdf_contents ="";
    employer = Employer.objects.get(employer_id = employer_id)
    if employer_id ==  employer.employer_id: 
        if employee_id != "*":
            pdf_contents = employeeCSVBuilder( start_time, end_time, employee_id, employer_id);
        else:
            pdf_contents = employerBuilder(start_time, end_time, employer_id, columns, show_incremental_hours, show_overtime_hours, show_holiday_hours, show_vacation_hours, show_sick_hours, show_holiday_hours_spent, show_vacation_hours_spent, show_sick_hours_spent );

        return HttpResponse(pdf_contents, content_type='application/pdf')
    tex.close()
    return render(request, 'payroll_data.html', {})
# Create your views here
@csrf_exempt
def getPayrollData(request):

    #Employer.objects.all().delete()
    #Employee.objects.all().delete()
    #Job.objects.all().delete()
    #PayPeriod.objects.all().delete()
    #employer1 = Employer(employer_id="12468",employer_name="Amazon", address="265 Lytton Ave.", pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), hash_key=make_password("HASHVALUE1"))
    #employer2 = Employer(employer_id="13492",employer_name="Microsoft", address="610 Mayfield Ave", pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), hash_key=make_password("HASHVALUE2"))
    #employee1 = Employee(employee_id="78932",employer_id="12468", employee_name = "Naveen Krishnamurthi", vacation_hours = 6.00, vacation_pay_rate = 60.00, sick_hours = 12.00, sick_pay_rate = 60.00, vacation_accrual_rate = 0.01, address="12795 Calle De La Siena, San Diego CA, 92130")
    #employee2 = Employee(employee_id="78777",employer_id="13492", employee_name = "Danial Shakeri", vacation_hours = 8.00, vacation_pay_rate = 62.00, sick_hours = 13.00, sick_pay_rate = 64.00, vacation_accrual_rate = 0.02, address="265 Westfield Ave., San Diego CA, 92130")
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
    # PayPeriod.objects.all().delete()
    # payPeriod1 = PayPeriod(employee_id="78777", job_id="8935", pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), hours = 40, overtime_hours = 2, incremental_hours_1 = 1, incremental_hours_2 = 2, incremental_hours_1_and_2 = 2, holiday_hours = 10, sick_hours = 12, vacation_hours = 12, holiday_hours_spent = 4, sick_hours_spent = 2, vacation_hours_spent = 1)
    # payPeriod2 = PayPeriod(employee_id="78777", job_id="8935", pay_start=datetime.datetime(2013, 12, 1, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 10, 17, 18, 40), hours = 40, overtime_hours = 2, incremental_hours_1 = 1, incremental_hours_2 = 2, incremental_hours_1_and_2 = 2, holiday_hours = 10, sick_hours = 12, vacation_hours = 12, holiday_hours_spent = 4, sick_hours_spent = 2, vacation_hours_spent = 1)
    # payPeriod3 = PayPeriod(employee_id="78412", job_id="8936", pay_start=datetime.datetime(2013, 12, 1, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 10, 17, 18, 40), hours = 40, overtime_hours = 2, incremental_hours_1 = 1, incremental_hours_2 = 2, incremental_hours_1_and_2 = 2, holiday_hours = 10, sick_hours = 12, vacation_hours = 12, holiday_hours_spent = 4, sick_hours_spent = 2, vacation_hours_spent = 1)
    # payPeriod4 = PayPeriod(employee_id="78932", job_id="7412", pay_start=datetime.datetime(2013, 12, 1, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 10, 17, 18, 40), hours = 40, overtime_hours = 2, incremental_hours_1 = 1, incremental_hours_2 = 2, incremental_hours_1_and_2 = 2, holiday_hours = 10, sick_hours = 12, vacation_hours = 12, holiday_hours_spent = 4, sick_hours_spent = 2, vacation_hours_spent = 1)

    # payPeriod1.save()
    # payPeriod2.save()
    # payPeriod3.save()
    # payPeriod4.save()
    json_data = json.loads(request.body)

    try:
        employer_id = json_data['employer_id']
        employer_key = json_data['key']
        start = json_data['start']
        end = json_data['end']
    except KeyError:
        raise Http404("EmployeeID, or employer info not found")
    if not auth_utils.check_employer(employer_id, employer_key):
        raise Http404("Invalid Employer ID/Key" )
    try:
        employee_id = json_data['employee_id']
    except KeyError:
        raise Http404("Employee info not found")

    columns = 0;
    try:
        show_incremental_hours = json_data['incremental_hours']
        columns += 3;
        show_incremental_hours = True
    except KeyError:
        show_incremental_hours = False 
    try:
        show_overtime_hours = json_data['overtime_hours']
        show_overtime_hours = True
        columns+=1;
    except KeyError:
        show_overtime_hours = False 
    try:
        show_holiday_hours = json_data['holiday_hours']
        show_holiday_hours = True
        columns+=1;
    except KeyError:
        show_holiday_hours = False
    try:
        show_vacation_hours = json_data['vacation_hours']
        columns+=1;
        show_vacation_hours = True
    except KeyError:
        show_vacation_hours = False
    try:
        show_sick_hours = json_data['sick_hours']
        columns+=1;
        show_sick_hours = True
    except KeyError:
        show_sick_hours = False
    try:
        show_holiday_hours_spent = json_data['holiday_hours_spent']
        columns+=1;
        show_holiday_hours_spent = True
    except KeyError:
        show_holiday_hours_spent = False
    try:
        show_vacation_hours_spent = json_data['vacation_hours_spent']
        columns+=1;
        show_vacation_hours_spent = True
    except KeyError:
        show_vacation_hours_spent = False
    try:
        show_sick_hours_spent = json_data['sick_hours_spent']
        columns+=1;
        show_sick_hours_spent = True
    except KeyError:
        show_sick_hours_spent = False

    start_time = datetime.datetime.strptime(start, "%m/%d/%y")
    end_time = datetime.datetime.strptime(end, "%m/%d/%y")
    tex_name =  "./" + employer_id + "_" + employee_id + ".tex" 
    pdf_name = employer_id + "_" + employee_id + ".pdf"
    
    tex = open( tex_name,'w')
    employer = Employer.objects.get(employer_id = employer_id)
    if employer_id ==  employer.employer_id: 
        if employee_id != "*":
            emplyee_tex = employeeBuilder( start_time, end_time, employee_id, employer_id);
            tex.write(emplyee_tex);
        else:
            employer_tex = employerBuilder(start_time, end_time, employer_id, columns, show_incremental_hours, show_overtime_hours, show_holiday_hours, show_vacation_hours, show_sick_hours, show_holiday_hours_spent, show_vacation_hours_spent, show_sick_hours_spent );
            tex.write(employer_tex);
        tex.close();
        call("pdflatex -output-directory payroll_app/static/pdf " + tex_name, shell=True)
        f = open("payroll_app/static/pdf/" + pdf_name , 'r')
        pdf_contents = f.read()
        f.close()
        return HttpResponse(pdf_contents, content_type='application/pdf')
    tex.close()
    return render(request, 'payroll_data.html', {})

#TODO: remove this since we should manually add companies
@csrf_exempt
def addCompany(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            employer_name = JSON_utils.addCompanyJSON(json.loads(request.body))
            return HttpResponse("Successfully created entry for %s." % employer_name) 
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")


@csrf_exempt
def addEmployee(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            json_data = json.loads(request.body)
            employee_name = JSON_utils.addEmployeeJSON(json_data)
            return HttpResponse("Successfully created entry for %s." % employee_name) 
        elif content_type == 'text/csv':
            json_data_list = csv_utils.parse_employee_csv(request.body)
            for json_data in json_data_list:
                JSON_utils.addEmployeeJSON(json_data)
            return HttpResponse("Added %d employees." % len(json_data_list))
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

@csrf_exempt
def addJob(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            json_data = json.loads(request.body)
            job_title = JSON_utils.addJobJSON(json_data)
            return HttpResponse("Successfully created entry for %s." % job_title) 
        elif content_type == 'text/csv':
            json_data_list = csv_utils.parse_job_csv(request.body)
            for json_data in json_data_list:
                JSON_utils.addJobJSON(json_data)
            return HttpResponse("Added %d jobs." % len(json_data_list))
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

@csrf_exempt
def addTimecardData(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            json_data = json.loads(request.body)
            num_cards = JSON_utils.addTimecardDataJSON(json_data)
            return HttpResponse("Successfully added %d timecards." % num_cards)
        elif content_type == 'text/csv':
            json_data = csv_utils.parse_timecard_csv(request.body)
            num_cards = JSON_utils.addTimecardDataJSON(json_data)
            return HttpResponse("Successfully added %d timecards." % num_cards)
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

@csrf_exempt
def addDailyTimecardData(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'text/csv':
            json_data = csv_utils.add_daily_timecard_data_csv(request.body)
            num_cards = JSON_utils.addTimecardDataJSON(json_data)
            return HttpResponse("Successfully added %d timecards." % num_cards)
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

@csrf_exempt
def addBonus(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            json_data = json.loads(request.body)
            employee_id = JSON_utils.addBonusJSON(json_data)
            return HttpResponse("Successfully added bonus for employee id %s." % employee_id)
        elif content_type == 'text/csv':
            json_data_list = csv_utils.parse_bonus_csv(request.body)
            for json_data in json_data_list:
                JSON_utils.addBonusJSON(json_data)
            return HttpResponse("Added %d bonuses." % len(json_data_list))
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")
