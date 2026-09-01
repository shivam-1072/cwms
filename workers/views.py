from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Worker, Attendance, Payroll, Expense, WorkLog, IncomingPayment
from sites.models import Site
from datetime import date, datetime, timedelta
from django.db import models
from django.db.models import Count, Sum, Q
from decimal import Decimal
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import pandas as pd
from io import BytesIO
import csv

# ============ HELPER FUNCTIONS ============
def is_admin(user):
    return user.is_superuser

def is_manager(user):
    return user.is_staff or user.is_superuser

# ============ WORKER VIEWS ============
@login_required
@user_passes_test(is_manager)
def worker_list(request):
    workers = Worker.objects.all()
    return render(request, 'workers/worker_list.html', {'workers': workers})

@login_required
@user_passes_test(is_admin)
def worker_create(request):
    sites = Site.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        joining_date = request.POST.get('joining_date')
        daily_wage = request.POST.get('daily_wage')
        site_id = request.POST.get('site')
        
        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, 'Phone number must be exactly 10 digits.')
            return render(request, 'workers/worker_form.html', {'sites': sites})
        
        worker = Worker.objects.create(
            name=name,
            phone=phone,
            joining_date=joining_date,
            daily_wage=daily_wage,
            site_id=site_id
        )
        messages.success(request, f'Worker {worker.name} added successfully!')
        return redirect('worker_list')
    
    return render(request, 'workers/worker_form.html', {'sites': sites})

@login_required
@user_passes_test(is_admin)
def worker_update(request, pk):
    worker = get_object_or_404(Worker, pk=pk)
    sites = Site.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        joining_date = request.POST.get('joining_date')
        daily_wage = request.POST.get('daily_wage')
        site_id = request.POST.get('site')
        
        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, 'Phone number must be exactly 10 digits.')
            return render(request, 'workers/worker_form.html', {'worker': worker, 'sites': sites})
        
        worker.name = name
        worker.phone = phone
        worker.joining_date = joining_date
        worker.daily_wage = daily_wage
        worker.site_id = site_id
        worker.save()
        messages.success(request, f'Worker {worker.name} updated successfully!')
        return redirect('worker_list')

    return render(request, 'workers/worker_form.html', {'worker': worker, 'sites': sites})

@login_required
@user_passes_test(is_admin)
def worker_delete(request, pk):
    worker = get_object_or_404(Worker, pk=pk)
    if request.method == 'POST':
        worker.delete()
        messages.success(request, 'Worker deleted successfully!')
        return redirect('worker_list')
    return render(request, 'workers/worker_confirm_delete.html', {'worker': worker})

# ============ ATTENDANCE VIEWS ============
@login_required
@user_passes_test(is_manager)
def attendance_list(request):
    attendances = Attendance.objects.select_related('worker__site').all()
    sites = Site.objects.all()

    site_filter = request.GET.get('site')
    if site_filter:
        attendances = attendances.filter(worker__site_id=site_filter)

    return render(request, 'workers/attendance_list.html', {
        'attendances': attendances,
        'sites': sites,
        'selected_site': site_filter,
    })

@login_required
@user_passes_test(is_manager)
def attendance_create(request):
    workers = Worker.objects.all()

    if request.method == 'POST':
        worker_id = request.POST.get('worker')
        status = request.POST.get('status')
        attendance_date = request.POST.get('date', date.today())
        extra_wage = request.POST.get('extra_wage', 0)

        worker = Worker.objects.get(id=worker_id)

        attendance, created = Attendance.objects.get_or_create(
            worker=worker,
            date=attendance_date,
            defaults={
                'status': status,
                'extra_wage': extra_wage,
            }
        )

        if not created:
            attendance.status = status
            attendance.extra_wage = extra_wage
            attendance.save()
            messages.info(request, f'Attendance updated for {worker.name}')
        else:
            messages.success(request, f'Attendance marked for {worker.name}')

        return redirect('attendance_list')

    return render(request, 'workers/attendance_form.html', {'workers': workers})

# ============ PAYROLL VIEWS ============
@login_required
@user_passes_test(is_admin)
def payroll_list(request):
    payrolls = Payroll.objects.select_related('worker').all()
    return render(request, 'workers/payroll_list.html', {'payrolls': payrolls})

@login_required
@user_passes_test(is_admin)
def generate_payroll(request):
    if request.method == 'POST':
        month = request.POST.get('month')
        month_date = datetime.strptime(month, '%Y-%m').date()

        workers = Worker.objects.all()

        for worker in workers:
            attendances = Attendance.objects.filter(
                worker=worker,
                date__year=month_date.year,
                date__month=month_date.month
            )
            
            total_days = (month_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            total_days = total_days.day

            paid_leaves = attendances.filter(status='paid_leave').count()
            unpaid_leaves = attendances.filter(status='unpaid_leave').count()
            present_days = attendances.filter(status='present').count()
            absent_days = attendances.filter(status='absent').count()
            
            total_extra_wage = attendances.filter(status='present').aggregate(total=models.Sum('extra_wage'))['total'] or 0

            working_days = present_days + paid_leaves
            daily_wage = worker.daily_wage
            gross_salary = (working_days * daily_wage) + total_extra_wage
            deductions = (absent_days + unpaid_leaves) * daily_wage
            net_salary = gross_salary - deductions

            payroll, created = Payroll.objects.update_or_create(
                worker=worker,
                month=month_date,
                defaults={
                    'total_days': total_days,
                    'working_days': working_days,
                    'paid_leaves': paid_leaves,
                    'unpaid_leaves': unpaid_leaves,
                    'daily_wage': daily_wage,
                    'gross_salary': gross_salary,
                    'deductions': deductions,
                    'net_salary': net_salary,
                }
            )

        messages.success(request, f'Payroll generated for {month_date.strftime("%B %Y")}')
        return redirect('payroll_list')

    return render(request, 'workers/generate_payroll.html')

@login_required
@user_passes_test(is_admin)
def export_payroll_csv(request):
    payrolls = Payroll.objects.select_related('worker').all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payroll_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Worker', 'Month', 'Working Days', 'Daily Wage', 'Gross Salary', 'Deductions', 'Net Salary'])

    for payroll in payrolls:
        writer.writerow([
            payroll.worker.name,
            payroll.month.strftime('%B %Y'),
            payroll.working_days,
            payroll.daily_wage,
            payroll.gross_salary,
            payroll.deductions,
            payroll.net_salary,
        ])

    return response

# ============ EXPENSE VIEWS ============
@login_required
@user_passes_test(is_manager)
def expense_list(request):
    expenses = Expense.objects.select_related('site').all()
    total_expense = expenses.aggregate(total=models.Sum('amount'))['total'] or 0

    category_totals = {}
    for category in ['material', 'food', 'fuel', 'equipment', 'other']:
        total = expenses.filter(category=category).aggregate(total=models.Sum('amount'))['total'] or 0
        category_totals[category] = total

    return render(request, 'workers/expense_list.html', {
        'expenses': expenses,
        'total_expense': total_expense,
        'category_totals': category_totals,
    })

@login_required
@user_passes_test(is_admin)
def expense_create(request):
    sites = Site.objects.all()

    if request.method == 'POST':
        site_id = request.POST.get('site')
        category = request.POST.get('category')
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        receipt = request.FILES.get('receipt')

        expense = Expense.objects.create(
            site_id=site_id,
            category=category,
            description=description,
            amount=amount,
            receipt=receipt
        )

        messages.success(request, f'Expense of ₹{amount} added successfully!')
        return redirect('expense_list')

    return render(request, 'workers/expense_form.html', {'sites': sites})

@login_required
@user_passes_test(is_admin)
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expense_list')
    return render(request, 'workers/expense_confirm_delete.html', {'expense': expense})

# ============ DASHBOARD VIEW ============
@login_required
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())
    
    filter_type = request.GET.get('filter', 'today')
    
    if filter_type == 'today':
        start_date = today
        end_date = today
    elif filter_type == 'weekly':
        start_date = week_start
        end_date = today
    elif filter_type == 'quarterly':
        start_date = today - timedelta(days=90)
        end_date = today
    elif filter_type == 'yearly':
        start_date = today - timedelta(days=365)
        end_date = today
    else:
        start_date = month_start
        end_date = today
    
    total_workers = Worker.objects.count()
    total_sites = Site.objects.count()
    
    today_attendance = Attendance.objects.filter(date=today).values('status').annotate(count=Count('status'))
    attendance_summary = {'present': 0, 'absent': 0, 'paid_leave': 0, 'unpaid_leave': 0}
    for item in today_attendance:
        attendance_summary[item['status']] = item['count']
    
    # ===== EXPENSES =====
    filtered_expenses = Expense.objects.filter(date__gte=start_date, date__lte=end_date)
    total_expense = filtered_expenses.aggregate(total=Sum('amount'))['total'] or 0

    # ===== PAYROLL =====
    payrolls_in_range = Payroll.objects.filter(month__gte=start_date, month__lte=end_date)
    monthly_payroll = payrolls_in_range.aggregate(total=Sum('net_salary'))['total'] or 0

    # ===== INCOMING PAYMENTS =====
    incoming_payments = IncomingPayment.objects.filter(
        received_date__gte=start_date,
        received_date__lte=end_date
    )
    total_incoming = incoming_payments.aggregate(total=Sum('amount'))['total'] or 0

    # ===== PROFIT / LOSS =====
    actual_profit = total_incoming - (total_expense + monthly_payroll)

    # ===== EXPENSES BY CATEGORY =====
    category_expenses = filtered_expenses.values('category').annotate(total=Sum('amount'))
    monthly_expense_totals = {'material': 0, 'food': 0, 'fuel': 0, 'equipment': 0, 'other': 0}
    for item in category_expenses:
        monthly_expense_totals[item['category']] = float(item['total'])
    
    total_spent = total_expense + monthly_payroll
    
    # ===== WEEKLY EXPENSES =====
    weekly_expenses = Expense.objects.filter(
        date__gte=week_start, date__lte=end_date
    ).values('date').annotate(total=Sum('amount')).order_by('date')
    weekly_expense_data = [
        {'date': item['date'].strftime('%Y-%m-%d'), 'amount': float(item['total'])}
        for item in weekly_expenses
    ]
    
    month_name = start_date.strftime('%B %Y')
    if filter_type == 'today':
        month_name = f"{today.strftime('%d %B %Y')} (Today)"
    elif filter_type == 'weekly':
        month_name = f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')} (Weekly)"
    elif filter_type == 'quarterly':
        month_name = f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')} (Quarterly)"
    elif filter_type == 'yearly':
        month_name = f"{start_date.strftime('%B %Y')} - {end_date.strftime('%B %Y')} (Yearly)"
    
    context = {
        'total_workers': total_workers,
        'total_sites': total_sites,
        'attendance_summary': attendance_summary,
        'monthly_expense_totals': monthly_expense_totals,
        'weekly_expense_data': weekly_expense_data,
        'monthly_payroll': float(monthly_payroll),
        'total_expense': float(total_expense),
        'total_spent': float(total_spent),
        'total_incoming': float(total_incoming),
        'actual_profit': float(actual_profit),
        'month_name': month_name,
        'filter_type': filter_type,
        'start_date': start_date.strftime('%d-%b-%Y'),
        'end_date': end_date.strftime('%d-%b-%Y'),
    }
    
    return render(request, 'workers/dashboard.html', context)

# ============ AUTHENTICATION VIEWS ============
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'workers/login.html')

@login_required
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('login')
    return render(request, 'workers/logout_confirm.html')

@login_required
@user_passes_test(is_manager)
def attendance_summary(request):
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    
    filter_type = request.GET.get('filter', 'weekly')
    
    if filter_type == 'today':
        start_date = today
        end_date = today
    elif filter_type == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif filter_type == 'monthly':
        start_date = today.replace(day=1)
        end_date = today
    elif filter_type == 'quarterly':
        start_date = today - timedelta(days=90)
        end_date = today
    elif filter_type == 'yearly':
        start_date = today - timedelta(days=365)
        end_date = today
    else:
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    
    workers = Worker.objects.all()
    total_workers = workers.count()
    
    worker_summary = []
    present_count = 0
    absent_count = 0
    leave_count = 0
    
    for worker in workers:
        attendances = Attendance.objects.filter(
            worker=worker,
            date__gte=start_date,
            date__lte=end_date
        )
        
        present = attendances.filter(status='present').count()
        absent = attendances.filter(status='absent').count()
        leaves = attendances.filter(status='paid_leave').count() + attendances.filter(status='unpaid_leave').count()
        total = attendances.count()
        
        present_count += present
        absent_count += absent
        leave_count += leaves
        
        worker_summary.append({
            'name': worker.name,
            'site': worker.site.name if worker.site else None,
            'present': present,
            'absent': absent,
            'leaves': leaves,
            'total': total,
        })
    
    if filter_type == 'today':
        period_label = f"{today.strftime('%d %B %Y')} (Today)"
    elif filter_type == 'weekly':
        period_label = f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')} (Weekly)"
    elif filter_type == 'monthly':
        period_label = f"{start_date.strftime('%B %Y')} (Monthly)"
    elif filter_type == 'quarterly':
        period_label = f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')} (Quarterly)"
    elif filter_type == 'yearly':
        period_label = f"{start_date.strftime('%B %Y')} - {end_date.strftime('%B %Y')} (Yearly)"
    else:
        period_label = f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')} (Weekly)"
    
    return render(request, 'workers/attendance_summary.html', {
        'worker_summary': worker_summary,
        'total_workers': total_workers,
        'present_count': present_count,
        'absent_count': absent_count,
        'leave_count': leave_count,
        'start_date': start_date,
        'end_date': end_date,
        'filter_type': filter_type,
        'period_label': period_label,
    })

@login_required
@user_passes_test(is_manager)
def attendance_export_summary(request):
    import csv
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    
    filter_type = request.GET.get('filter', 'weekly')
    
    if filter_type == 'today':
        start_date = today
        end_date = today
    elif filter_type == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif filter_type == 'monthly':
        start_date = today.replace(day=1)
        end_date = today
    elif filter_type == 'quarterly':
        start_date = today - timedelta(days=90)
        end_date = today
    elif filter_type == 'yearly':
        start_date = today - timedelta(days=365)
        end_date = today
    else:
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_summary_{start_date.strftime("%Y-%m-%d")}_to_{end_date.strftime("%Y-%m-%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Worker', 'Site', 'Present', 'Absent', 'Leaves', 'Total Days'])
    
    workers = Worker.objects.all()
    for worker in workers:
        attendances = Attendance.objects.filter(
            worker=worker,
            date__gte=start_date,
            date__lte=end_date
        )
        
        present = attendances.filter(status='present').count()
        absent = attendances.filter(status='absent').count()
        leaves = attendances.filter(status='paid_leave').count() + attendances.filter(status='unpaid_leave').count()
        total = attendances.count()
        
        writer.writerow([
            worker.name,
            worker.site.name if worker.site else 'Not Assigned',
            present,
            absent,
            leaves,
            total,
        ])
    
    return response

# ============ WORKLOG VIEWS ============
@login_required
@user_passes_test(is_admin)
def worklog_list(request):
    work_logs = WorkLog.objects.select_related('site').all()
    sites = Site.objects.all()
    
    site_filter = request.GET.get('site')
    if site_filter:
        work_logs = work_logs.filter(site_id=site_filter)
    
    return render(request, 'workers/worklog_list.html', {
        'work_logs': work_logs,
        'sites': sites,
        'selected_site': site_filter,
    })

@login_required
@user_passes_test(is_admin)
def worklog_create(request):
    sites = Site.objects.all()
    
    if request.method == 'POST':
        site_id = request.POST.get('site')
        work_done = request.POST.get('work_done')
        pending_work = request.POST.get('pending_work')
        worker_count = request.POST.get('worker_count', 0)
        
        worklog = WorkLog.objects.create(
            site_id=site_id,
            work_done=work_done,
            pending_work=pending_work,
            worker_count=worker_count
        )
        messages.success(request, 'Work log added successfully!')
        return redirect('worklog_list')
    
    return render(request, 'workers/worklog_form.html', {'sites': sites})

@login_required
@user_passes_test(is_admin)
def worklog_update(request, pk):
    worklog = get_object_or_404(WorkLog, pk=pk)
    sites = Site.objects.all()
    
    if request.method == 'POST':
        worklog.site_id = request.POST.get('site')
        worklog.work_done = request.POST.get('work_done')
        worklog.pending_work = request.POST.get('pending_work')
        worklog.worker_count = request.POST.get('worker_count', 0)
        worklog.save()
        messages.success(request, 'Work log updated successfully!')
        return redirect('worklog_list')
    
    return render(request, 'workers/worklog_form.html', {
        'worklog': worklog,
        'sites': sites,
    })

@login_required
@user_passes_test(is_admin)
def worklog_delete(request, pk):
    worklog = get_object_or_404(WorkLog, pk=pk)
    if request.method == 'POST':
        worklog.delete()
        messages.success(request, 'Work log deleted successfully!')
        return redirect('worklog_list')
    return render(request, 'workers/worklog_confirm_delete.html', {'worklog': worklog})

# ============ PAYMENT SLIP VIEWS ============
@login_required
def payslip_form(request):
    workers = Worker.objects.all()
    return render(request, 'workers/payslip_form.html', {'workers': workers})

@login_required
def generate_payslip(request):
    if request.method == 'POST':
        worker_id = request.POST.get('worker')
        month = request.POST.get('month')
        format_type = request.POST.get('format', 'pdf')

        if not worker_id or not month:
            messages.error(request, 'Please select worker and month.')
            return redirect('payslip_form')

        worker = get_object_or_404(Worker, id=worker_id)
        month_date = datetime.strptime(month, '%Y-%m').date()

        payroll = Payroll.objects.filter(worker=worker, month=month_date).first()

        if not payroll:
            messages.error(request, f'No payroll found for {worker.name} in {month_date.strftime("%B %Y")}')
            return redirect('payslip_form')

        if format_type == 'pdf':
            return generate_pdf_payslip(worker, payroll, month_date)
        else:
            return generate_excel_payslip(worker, payroll, month_date)

    return redirect('payslip_form')

def generate_pdf_payslip(worker, payroll, month_date):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payslip_{worker.name}_{month_date.strftime("%B_%Y")}.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, height - 1*inch, "CONSTRUCTION WORKFORCE MANAGEMENT SYSTEM")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 1.5*inch, f"PAYMENT SLIP - {month_date.strftime('%B %Y')}")

    c.line(1*inch, height - 1.8*inch, 7.5*inch, height - 1.8*inch)

    c.setFont("Helvetica", 12)
    y = height - 2.3*inch
    details = [
        f"Worker Name: {worker.name}",
        f"Phone: {worker.phone}",
        f"Site: {worker.site.name}",
        f"Daily Wage: ₹{worker.daily_wage}",
    ]
    for detail in details:
        c.drawString(1*inch, y, detail)
        y -= 0.4*inch

    c.setFont("Helvetica-Bold", 12)
    y -= 0.3*inch
    c.drawString(1*inch, y, "SALARY DETAILS")
    y -= 0.5*inch

    c.setFont("Helvetica", 11)
    salary_details = [
        ("Working Days", payroll.working_days),
        ("Gross Salary", f"₹{payroll.gross_salary}"),
        ("Deductions", f"₹{payroll.deductions}"),
        ("Net Salary", f"₹{payroll.net_salary}"),
    ]
    for label, value in salary_details:
        c.drawString(1*inch, y, f"{label}: {value}")
        y -= 0.4*inch

    c.setFont("Helvetica", 10)
    c.drawString(1*inch, 1*inch, f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    c.drawString(5.5*inch, 1*inch, "Payment Slip")

    c.save()
    return response

def generate_excel_payslip(worker, payroll, month_date):
    data = {
        'Worker': [worker.name],
        'Phone': [worker.phone],
        'Site': [worker.site.name],
        'Daily Wage': [float(worker.daily_wage)],
        'Working Days': [payroll.working_days],
        'Gross Salary': [float(payroll.gross_salary)],
        'Deductions': [float(payroll.deductions)],
        'Net Salary': [float(payroll.net_salary)],
        'Month': [month_date.strftime('%B %Y')],
    }

    df = pd.DataFrame(data)
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Payslip')

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="payslip_{worker.name}_{month_date.strftime("%B %Y")}.xlsx"'

    return response

@login_required
def incoming_create(request):
    sites = Site.objects.all()
    
    if request.method == 'POST':
        site_id = request.POST.get('site')
        amount = request.POST.get('amount')
        description = request.POST.get('description', '')
        
        IncomingPayment.objects.create(
            site_id=site_id,
            amount=amount,
            description=description
        )
        messages.success(request, f'₹{amount} added to incoming payments!')
        return redirect('dashboard')
    
    return render(request, 'workers/incoming_form.html', {'sites': sites})

@login_required
def incoming_list(request):
    payments = IncomingPayment.objects.select_related('site').all()
    return render(request, 'workers/incoming_list.html', {'payments': payments})