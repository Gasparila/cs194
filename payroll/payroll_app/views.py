from django.db import models
from django.contrib import auth, messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
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
    if not checkEmployer(employer_id, employer_key):
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
    # json_data = json.loads(request.body)

    try:
        employer_id = json_data['employer_id']
        employer_key = json_data['key']
        start = json_data['start']
        end = json_data['end']
    except KeyError:
        raise Http404("EmployeeID, or employer info not found")
    if not checkEmployer(employer_id, employer_key):
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

def checkEmployer(employer_id, employer_key):
    employer = Employer.objects.get(employer_id = employer_id)
    return check_password(employer_key, employer.hash_key)

#TODO: remove this since we should manually add companies
@csrf_exempt
def addCompany(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            employer_name = addCompanyJSON(json.loads(request.body))
            return HttpResponse("Successfully created entry for %s." % employer_name) 
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

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

@csrf_exempt
def addEmployee(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            json_data = json.loads(request.body)
            employee_name = addEmployeeJSON(json_data)
            return HttpResponse("Successfully created entry for %s." % employee_name) 
        elif content_type == 'text/csv':
            json_data_list = parse_employee_csv(request.body)
            for json_data in json_data_list:
                addEmployeeJSON(json_data)
            return HttpResponse("Added %d employees." % len(json_data_list))
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

def parse_employee_csv(csv_file):
    data_list = []
    metadata = {}
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


def addEmployeeJSON(json_data):
    try:
        employee_id = json_data['employee_id']
        if Employee.objects.filter(employee_id = employee_id).exists():
            raise Http404("Employee %s Already Exists" % employee_id)
        employer_key = json_data['employer_key']
    except KeyError:
        raise Http404("EmployeeID, or employer info not found")
    if not checkEmployer(employer_id, employer_key):
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

@csrf_exempt
def addJob(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            json_data = json.loads(request.body)
            job_title = addJobJSON(json_data)
            return HttpResponse("Successfully created entry for %s." % job_title) 
        elif content_type == 'text/csv':
            json_data_list = parse_job_csv(request.body)
            for json_data in json_data_list:
                addJobJSON(json_data)
            return HttpResponse("Added %d jobs." % len(json_data_list))
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

def parse_job_csv(csv_file):
    data_list = []
    lines = csv_file.splitlines()
    first = True
    metadata = {}
    for line in lines:
        obj = {}
        values = line.split(',')
        if first:
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
    if not checkEmployer(employer_id, employer_key) :
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

@csrf_exempt
def addTimecardData(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            json_data = json.loads(request.body)
            num_cards = addTimecardDataJSON(json_data)
            return HttpResponse("Successfully added %d timecards." % num_cards)
        elif content_type == 'text/csv':
            json_data = parse_timecard_csv(request.body)
            num_cards = addTimecardDataJSON(json_data)
            return HttpResponse("Successfully added %d timecards." % num_cards)
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

def parse_timecard_csv(csv_file):
    data = {}
    data_list = []
    lines = csv_file.splitlines()
    first = True
    for line in lines:
        obj = {}
        values = line.split(',')
        if first:
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

def addTimecardDataJSON(json_data):
    try:
        pay_period = json_data['pay_period']
        employer_id = json_data['employer_id']
        employer_key = json_data['employer_key']
        timecard_entries = json_data['timecard_data']
    except KeyError:
        raise Http404("Pay period or employer info not found")
    if not checkEmployer(employer_id, employer_key) :
        raise Http404("Invalid Employer ID/Key")
    for json_entry in timecard_entries:
        entry = parseTimecardData(json_entry)
        entry.pay_start = datetime.datetime.strptime(pay_period["start"], "%m/%d/%y")
        entry.pay_end = datetime.datetime.strptime(pay_period["end"], "%m/%d/%y")
        entry.save();
    return len(timecard_entries)

@csrf_exempt
def addDailyTimecardData(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'text/csv':
            json_data = add_daily_timecard_data_csv(request.body)
            num_cards = addTimecardDataJSON(json_data)
            return HttpResponse("Successfully added %d timecards." % num_cards)
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

def add_daily_timecard_data_csv(csv_file):
    data = {}
    data_list = []
    lines = csv_file.splitlines()
    first = True
    days_in_period = 0
    for line in lines:
        obj = {}
        values = line.split(',')
        if first:
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

def calculate_overtime(daily_hours, weekly_hours):
    overtime_hours = 0
    if daily_hours > 8:
        overtime_hours = daily_hours - 8
    weekly_hours += daily_hours - overtime_hours
    if weekly_hours > 40:
        overtime_hours += weekly_hours - 40
        weekly_hours = 40
    return over_time

@csrf_exempt
def addBonus(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            json_data = json.loads(request.body)
            employee_id = addBonusJSON(json_data)
            return HttpResponse("Successfully added bonus for employee id %s." % employee_id)
        elif content_type == 'text/csv':
            json_data_list = parse_bonus_csv(request.body)
            for json_data in json_data_list:
                addBonusJSON(json_data)
            return HttpResponse("Added %d bonuses." % len(json_data_list))
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

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
    if not checkEmployer(employer_id, employer_key) :
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
