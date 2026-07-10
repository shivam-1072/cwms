from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Worker
from sites.models import Site

def worker_list(request):
    workers = Worker.objects.all()
    return render(request, 'workers/worker_list.html', {'workers': workers})

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

def worker_delete(request, pk):
    worker = get_object_or_404(Worker, pk=pk)
    if request.method == 'POST':
        worker.delete()
        messages.success(request, 'Worker deleted successfully!')
        return redirect('worker_list')
    return render(request, 'workers/worker_confirm_delete.html', {'worker': worker})


from .models import Worker, Attendance
from datetime import date

def attendance_list(request):
    attendances = Attendance.objects.select_related('worker').all()
    return render(request, 'workers/attendance_list.html', {'attendances': attendances})

def attendance_create(request):
    workers = Worker.objects.all()

    if request.method == 'POST':
        worker_id = request.POST.get('worker')
        status = request.POST.get('status')
        attendance_date = request.POST.get('date', date.today())

        worker = Worker.objects.get(id=worker_id)

        # Check if attendance already exists for this worker on this date
        attendance, created = Attendance.objects.get_or_create(
            worker=worker,
            date=attendance_date,
            defaults={'status': status}
        )

        if not created:
            # Update existing attendance
            attendance.status = status
            attendance.save()
            messages.info(request, f'Attendance updated for {worker.name}')
        else:
            messages.success(request, f'Attendance marked for {worker.name}')

        return redirect('attendance_list')

    return render(request, 'workers/attendance_form.html', {'workers': workers})
