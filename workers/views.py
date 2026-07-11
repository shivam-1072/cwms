from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Worker, Attendance, Payroll, Expense, UserProfile
from sites.models import Site
from datetime import date, datetime, timedelta
from django.db import models
from django.db.models import Count, Sum, Q
from decimal import Decimal
from django.http import HttpResponse
from django.utils import timezone
import csv

# ============ WORKER VIEWS ============
@login_required
def worker_list(request):
    workers = Worker.objects.all()
    return render(request, 'workers/worker_list.html', {'workers': workers})

@login_required
def worker_create(request):
    sites = Site.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        joining_date = request.POST.get('joining_date')
        daily_wage = request.POST.get('daily_wage')
        site_id = request.POST.get('site')

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
def worker_update(request, pk):
    worker = get_object_or_404(Worker, pk=pk)
    sites = Site.objects.all()

    if request.method == 'POST':
        worker.name = request.POST.get('name')
        worker.phone = request.POST.get('phone')
        worker.joining_date = request.POST.get('joining_date')
        worker.daily_wage = request.POST.get('daily_wage')
        worker.site_id = request.POST.get('site')
        worker.save()
        messages.success(request, f'Worker {worker.name} updated successfully!')
        return redirect('worker_list')

    return render(request, 'workers/worker_form.html', {'worker': worker, 'sites': sites})

@login_required
def worker_delete(request, pk):
    worker = get_object_or_404(Worker, pk=pk)
    if request.method == 'POST':
        worker.delete()
        messages.success(request, 'Worker deleted successfully!')
        return redirect('worker_list')
    return render(request, 'workers/worker_confirm_delete.html', {'worker': worker})

# ============ ATTENDANCE VIEWS ============
@login_required
def attendance_list(request):
    attendances = Attendance.objects.select_related('worker').all()
    return render(request, 'workers/attendance_list.html', {'attendances': attendances})

@login_required
def attendance_create(request):
    workers = Worker.objects.all()

    if request.method == 'POST':
        worker_id = request.POST.get('worker')
        status = request.POST.get('status')
        attendance_date = request.POST.get('date', date.today())

        worker = Worker.objects.get(id=worker_id)

        attendance, created = Attendance.objects.get_or_create(
            worker=worker,
            date=attendance_date,
            defaults={'status': status}
        )

        if not created:
            attendance.status = status
            attendance.save()
            messages.info(request, f'Attendance updated for {worker.name}')
        else:
            messages.success(request, f'Attendance marked for {worker.name}')

        return redirect('attendance_list')

    return render(request, 'workers/attendance_form.html', {'workers': workers})

# ============ PAYROLL VIEWS ============
@login_required
def payroll_list(request):
    payrolls = Payroll.objects.select_related('worker').all()
    return render(request, 'workers/payroll_list.html', {'payrolls': payrolls})

@login_required
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

            working_days = present_days + paid_leaves
            daily_wage = worker.daily_wage
            gross_salary = working_days * daily_wage
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

    total_workers = Worker.objects.count()
    total_sites = Site.objects.count()

    monthly_attendance = Attendance.objects.filter(
        date__gte=month_start
    ).values('status').annotate(count=Count('status'))

    attendance_summary = {
        'present': 0,
        'absent': 0,
        'paid_leave': 0,
        'unpaid_leave': 0,
    }
    for item in monthly_attendance:
        attendance_summary[item['status']] = item['count']

    monthly_expenses = Expense.objects.filter(
        date__gte=month_start
    ).values('category').annotate(total=Sum('amount'))

    monthly_expense_totals = {
        'material': 0,
        'food': 0,
        'fuel': 0,
        'equipment': 0,
        'other': 0,
    }
    for item in monthly_expenses:
        monthly_expense_totals[item['category']] = float(item['total'])

    weekly_expenses = Expense.objects.filter(
        date__gte=week_start
    ).values('date').annotate(total=Sum('amount')).order_by('date')

    weekly_expense_data = [
        {'date': item['date'].strftime('%Y-%m-%d'), 'amount': float(item['total'])}
        for item in weekly_expenses
    ]

    monthly_payroll = Payroll.objects.filter(
        month=month_start
    ).aggregate(total=Sum('net_salary'))['total'] or 0

    total_expense = monthly_expenses.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'total_workers': total_workers,
        'total_sites': total_sites,
        'attendance_summary': attendance_summary,
        'monthly_expense_totals': monthly_expense_totals,
        'weekly_expense_data': weekly_expense_data,
        'monthly_payroll': float(monthly_payroll),
        'total_expense': float(total_expense),
        'profit_loss': float(total_expense) - float(monthly_payroll),
        'month_name': month_start.strftime('%B %Y'),
    }

    return render(request, 'workers/dashboard.html', context)

# ============ AUTHENTICATION VIEWS (No login_required) ============
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

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'workers/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'workers/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user)

        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')

    return render(request, 'workers/register.html')
