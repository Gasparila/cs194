from payroll_app.models import Employer, Employee, Job, BonusPay, PayPeriod, AuthUser
import datetime
from subprocess import call


def employeeBuilder(start_time, end_time, employee_id, employer_id):
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
                    incremental_pay1 =  payperiod.incremental_hours_1 * (job.incremental_hours_1);
                    total = total + incremental_pay1
                    incremental_row1 = "Incremental 1 & " + str(payperiod.incremental_hours_1) + " & " + str((job.incremental_hours_1)) + " & " + str(incremental_pay1) + " \\\\\n\\hline\n"   
                    tex_file +=incremental_row1; 
                if payperiod.incremental_hours_2 > 0:
                    incremental_pay2 =  payperiod.incremental_hours_2 * (job.incremental_hours_2);
                    incremental_row2 = "Incremental 2 & " + str(payperiod.incremental_hours_2) + " & " + str(job.incremental_hours_2) + " & " + str(incremental_pay2) + " \\\\\n\\hline\n"   
                    total = total + incremental_pay2
                    tex_file +=incremental_row2;
                if payperiod.vacation_hours_spent > 0:
                    vacation_rate = job.base_rate
                    vacation_pay =  payperiod.vacation_hours_spent * (vacation_rate);
                    total = total + vacation_pay
                    vacation_row = "Vacation & " + str(payperiod.vacation_hours_spent) + " & " + str((vacation_rate)) + " & " + str(vacation_pay) + " \\\\\n\\hline\n"   
                    tex_file += vacation_row; 
                if payperiod.sick_hours_spent > 0:
                    sick_rate = job.base_rate
                    sick_pay =  payperiod.sick_hours_spent * (sick_rate);
                    total = total + sick_pay
                    sick_row = "Sick & " + str(payperiod.sick_hours_spent) + " & " + str((sick_rate)) + " & " + str(sick_pay) + " \\\\\n\\hline\n"   
                    tex_file += sick_row;
                if payperiod.holiday_hours_spent > 0:
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
    bonuses = BonusPay.objects.all().filter(date_given__gte = start_time);
    bonuses = bonuses.filter(date_given__lte = end_time + datetime.timedelta(days=1));
    bonuses = bonuses.filter(employee_id = employee.employee_id);
    if bonuses:
        tex_file += "Bonuses: \\\\\n\\begin{table}[htb]\n\\begin{tabular}{| l | l | }\n\\hline\n\\textbf{Date Bonus Given} & \\textbf{Amount} \\\\\n\\hline\n"
        for bonus in bonuses:
            tex_file +=  str(bonus.date_given.strftime('%m/%d/%Y')) + "& " + str(bonus.amount) + "\\\\\n\\hline\n";
        table_end = "\\end{tabular}\n\\end{table}\n\n\n"
        tex_file += table_end;
    tex_file += "\\end{document}"
    return tex_file

def employerBuilder(start_time, end_time, employer_id):
    employer = Employer.objects.get(employer_id = employer_id)
    tex_file = "\\documentclass[14pt]{article}\n\\newcommand{\\tab}[1]{\\hspace{.2\\textwidth}\\rlap{1}}\n\\begin{document}\n\\setlength{\\parindent}{0pt}\n\n"
    employees = Employee.objects.all().filter(employer_id = employer_id)
    employer_info = "To: " + employer.employer_name + "\\\\\nAddress: " + employer.address + "\\\\\n\n"  
    tex_file += employer_info
    table = "| l | l | l | l | l | l |"
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
                    total_hours = payperiod.sick_hours_spent + payperiod.holiday_hours_spent + payperiod.vacation_hours_spent + payperiod.hours + payperiod.overtime_hours 
                    base_pay =  payperiod.hours * job.base_rate;
                    total = base_pay;
                    if payperiod.overtime_hours > 0: 
                        overtime_pay =  payperiod.overtime_hours * (Decimal(job.base_rate) * Decimal(1.5));
                        total = total + overtime_pay
                    if payperiod.incremental_hours_1 > 0:
                        incremental_pay1 =  payperiod.incremental_hours_1 * (job.incremental_hours_1);
                        total = total + incremental_pay1
                    if payperiod.incremental_hours_2 > 0:
                        incremental_pay2 =  payperiod.incremental_hours_2 * (job.incremental_hours_2);
                        total = total + incremental_pay2;
                    if payperiod.vacation_hours_spent > 0:
                        vacation_rate = job.base_rate
                        vacation_pay =  payperiod.vacation_hours_spent * (vacation_rate);
                        total = total + vacation_pay
                    if payperiod.sick_hours_spent > 0:
                        sick_rate = job.base_rate
                        sick_pay =  payperiod.sick_hours_spent * (sick_rate);
                        total = total + sick_pay
                    if payperiod.holiday_hours_spent > 0:
                        holiday_pay_rate  = job.base_rate
                        holiday_pay =  payperiod.holiday_hours_spent * (holiday_pay_rate);
                        total = total + holiday_pay   
                    allTotal += total;
                    all_row = all_row + "" + str(total_hours) + " & " + str(total) + "\\\\\n\\hline\n"    
                    tex_file += all_row;                
    tex_file += "\\textbf{Total:} & & & & & \\textbf{\\$" + str(allTotal) + "}\\\\\n\\hline\n"
    end_table = "\\hline\n\\end{tabular}\n\\end{table}\n\n\n";
    tex_file += end_table;
    bonuses = BonusPay.objects.all().filter(date_given__gte = start_time);
    bonuses = bonuses.filter(date_given__lte = end_time + datetime.timedelta(days=1));
    if bonuses:
        tex_file += "Bonuses: \\\\\n\\begin{table}[htb]\n\\begin{tabular}{| l | l | l | l |}\n\\hline\n\\textbf{Employee ID} & \\textbf{Employee} & \\textbf{Date Bonus Given} & \\textbf{Amount} \\\\\n\\hline\n"
        for bonus in bonuses:
            for employee in employees:
                if employee.employee_id == bonus.employee_id:
                    tex_file += employee.employee_id + " & " + employee.employee_name + " & " + str(bonus.date_given.strftime('%m/%d/%Y')) + "& " + str(bonus.amount) + "\\\\\n\\hline\n";
        table_end = "\\end{tabular}\n\\end{table}\n\n\n"
        tex_file += table_end;
    tex_file += "\\end{document}"
    return tex_file

def buildPDF(employer_id, employee_id, start_time, end_time, pdf_contents, pdf_name):
    tex_name =  "./" + employer_id + "_" + employee_id + ".tex" 
    tex = open(tex_name,'w')
    if pdf_contents == "":
        employer = Employer.objects.get(employer_id = employer_id)
        if employee_id != "*":
            employee_tex = employeeBuilder(start_time, end_time, employee_id, employer_id);
            tex.write(employee_tex);
        else:
            employer_tex = employerBuilder(start_time, end_time, employer_id);
            tex.write(employer_tex);
    else:
        tex_file = "\\documentclass[14pt]{article}\n\\newcommand{\\tab}[1]{\\hspace{.2\\textwidth}\\rlap{1}}\n\\begin{document}\n\\setlength{\\parindent}{0pt}\n\n"
        tex_file += pdf_contents + "\n\\end{document}";
        tex.write(tex_file); 
    tex.close();
    call("pdflatex -output-directory payroll_app/static/pdf " + tex_name, shell=True)
    f = open("payroll_app/static/pdf/" + pdf_name , 'r')
    pdf_contents = f.read()
    f.close()
    return pdf_contents

def employerCSVBuilder(start_time, end_time, employer_id, employee_name):
    employer = Employer.objects.get(employer_id = employer_id)
    employees = Employee.objects.all().filter(employer_id = employer_id)
    if not str(employee_name).isspace() and str(employee_name):
        employees = employees.filter(employee_name__icontains = employee_name);

    employer_info = "To:, " + employer.employer_name + "\nAddress:, " + employer.address + "\n\n"  
    tex_file = employer_info
    allTotal = 0;
    table_start = "Employee, Job, Start Date, End Date, Base Hours, Base Rate, Base Payment, Overtime Hours, Overtime Rate, Overtime Payment, Incremental 1 Hours, Incremntal 1 Rate, Incremntal 1 Payment, Incremental 2 Hours, Incremntal 2 Rate, Incremntal 2 Payment, Vacation Hours Spent, Vacation Rate, Vacation Payment, Sick Hours Spent, Sick Rate, Sick Payment, Holiday Hours Spent, Holiday Rate, Holiday Payment, Sick Hours Acquired, Vacation Hours Acquired, Total Hours, Total Payment \n"      
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
                    " Total Hours, Total Payment \n"      
                    all_row = employee.employee_name + ", " + job.job_title + ", " + str(payperiod.pay_start.strftime('%m/%d/%Y')) + ", " + str(payperiod.pay_end.strftime('%m/%d/%Y')) + ", "
                    total_hours = payperiod.sick_hours_spent + payperiod.holiday_hours_spent + payperiod.vacation_hours_spent + payperiod.hours + payperiod.overtime_hours 
                    base_pay =  payperiod.hours * job.base_rate;
                    all_row += str(payperiod.hours) + ", " + str(job.base_rate) + ", " + str(base_pay) + ", ";
                    total = base_pay;
                    overtime_pay =  payperiod.overtime_hours * (Decimal(job.base_rate) * Decimal(1.5));
                    all_row += str(payperiod.overtime_hours) + ", " + str(Decimal(job.base_rate) * Decimal(1.5))+ ", " + str(overtime_pay) + ", ";
                    total = total + overtime_pay
                    incremental_pay1 =  payperiod.incremental_hours_1 * (job.incremental_hours_1);
                    all_row += str(payperiod.incremental_hours_1) + ", " + str(job.incremental_hours_1)+ ", " + str(incremental_pay1)+ ", " 
                    total = total + incremental_pay1
                    incremental_pay2 =  payperiod.incremental_hours_2 * (job.incremental_hours_2);
                    all_row += str(payperiod.incremental_hours_2) + ", " + str(job.incremental_hours_2)+ ", " + str(incremental_pay2)+ ", " 
                    total = total + incremental_pay2;
                    vacation_rate = job.base_rate
                    vacation_pay =  payperiod.vacation_hours_spent * (vacation_rate);
                    all_row += str(payperiod.vacation_hours_spent) + ", " + str(vacation_rate) + ", " + str(vacation_pay) + ", "
                    total = total + vacation_pay
                    sick_rate = job.base_rate
                    sick_pay =  payperiod.sick_hours_spent * (sick_rate);
                    all_row += str(payperiod.sick_hours_spent) + ", " + str(sick_rate) + ", " + str(sick_pay) + ", "
                    total = total + sick_pay
                    holiday_pay_rate  = job.base_rate
                    holiday_pay =  payperiod.holiday_hours_spent * (holiday_pay_rate);
                    all_row += str(payperiod.holiday_hours_spent) + ", " + str(holiday_pay_rate) + ", " + str(holiday_pay) + ", "                    
                    total = total + holiday_pay
                    all_row += str(payperiod.sick_hours) + ", " + str(payperiod.vacation_hours) + ", ";
                    allTotal += total;
                    all_row += str(total_hours) + ", " + str(total) + "\n";    
                    tex_file += all_row;   
    tex_file += ",,,,,,,,,,,,,,,,,,,,,,,,,,, Total:, " + str(allTotal) +" \n\n\n"
    bonuses = BonusPay.objects.all().filter(date_given__gte = start_time);
    bonuses = bonuses.filter(date_given__lte = end_time);
    if bonuses:
        tex_file += "Bonuses:\n Employee ID, Employee, Date Bonus Given, Amount \n"
        for bonus in bonuses:
            for employee in employees:
                if bonus.employee_id == employee.employee_id:
                    tex_file += employee.employee_id + ", " + employee.employee_name + ", " + str(bonus.date_given.strftime('%m/%d/%Y'))+ ", " + str(bonus.amount) + "\n"; 
    return tex_file

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
    employer_info = "From:, " + employer.employer_name + "\nAddress:, " + employer.address + "\n\n"  
    tex_file += employer_info
    for payperiod in payperiod1:
        for job in jobs:
            if job.job_id == payperiod.job_id:
                payPeriod_info = "Pay Period:, " + str(payperiod.pay_start.strftime('%m/%d/%Y')) + ", to, " + str(payperiod.pay_end.strftime('%m/%d/%Y')) + " \nJob:, " + job.job_title + " \n"
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
                    incremental_pay1 =  payperiod.incremental_hours_1 * (job.incremental_hours_1);
                    total = total + incremental_pay1
                    incremental_row1 = "Incremental 1, " + str(payperiod.incremental_hours_1) + ", " + str((job.incremental_hours_1)) + ", " + str(incremental_pay1) + "\n"   
                    tex_file +=incremental_row1; 
                if payperiod.incremental_hours_2 > 0:
                    incremental_pay2 =  payperiod.incremental_hours_2 * (job.incremental_hours_2);
                    incremental_row2 = "Incremental 2, " + str(payperiod.incremental_hours_2) + ", " + str((job.incremental_hours_2)) + ", " + str(incremental_pay2) + "\n"   
                    total = total + incremental_pay2
                    tex_file +=incremental_row2;
                if payperiod.vacation_hours_spent > 0:
                    vacation_rate = job.base_rate
                    vacation_pay =  payperiod.vacation_hours_spent * (vacation_rate);
                    total = total + vacation_pay
                    vacation_row = "Vacation, " + str(payperiod.vacation_hours_spent) + ", " + str((vacation_rate)) + ", " + str(vacation_pay) + "\n"   
                    tex_file += vacation_row; 
                if payperiod.sick_hours_spent > 0:
                    sick_rate = job.base_rate
                    sick_pay =  payperiod.sick_hours_spent * (sick_rate);
                    total = total + sick_pay
                    sick_row = "Sick, " + str(payperiod.sick_hours_spent) + ", " + str((sick_rate)) + ", " + str(sick_pay) + "\n"   
                    tex_file += sick_row;
                if payperiod.holiday_hours_spent > 0:
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
                sick_row = "Sick Hours, " + str(payperiod.sick_hours) + ", " + str((employee.sick_hours)) +"\n\n\n" 
                tex_file += vacation_row
                tex_file += sick_row

    bonuses = BonusPay.objects.all().filter(date_given__gte = start_time);
    bonuses = bonuses.filter(date_given__lte = end_time );
    bonuses = bonuses.filter(employee_id = employee.employee_id);
    if bonuses:
        tex_file += "Bonuses:\n Date Bonus Given, Amount \n"
        for bonus in bonuses:
            tex_file +=  str(bonus.date_given.strftime('%m/%d/%Y')) + ", " + str(bonus.amount) + "\n"; 
    return tex_file

def buildCSV(employer_id, employee_id, employee_name, start_time, end_time, csv_contents, csv_name):
    if csv_contents == "":    
        employer = Employer.objects.get(employer_id = employer_id)
        if employer_id ==  employer.employer_id: 
            if employee_id != "*":
                csv_contents = employeeCSVBuilder(start_time, end_time, employee_id, employer_id);
            else:
                csv_contents = employerCSVBuilder(start_time, end_time, employer_id, employee_name);
    return csv_contents

