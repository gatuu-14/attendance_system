from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.db.models import Q, Count, Case, When, Value, IntegerField
from .models import Student, Attendance
from .forms import StudentForm, AttendanceForm, DateRangeForm
from datetime import datetime, timedelta

# Authentication Views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Welcome {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'students/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('login')

# Dashboard
@login_required
def dashboard(request):
    total_students = Student.objects.filter(is_active=True).count()
    
    today = timezone.now().date()
    today_attendance = Attendance.objects.filter(date=today).count()
    present_today = Attendance.objects.filter(date=today, status='P').count()
    absent_today = Attendance.objects.filter(date=today, status='A').count()
    late_today = Attendance.objects.filter(date=today, status='L').count()
    
    # Last 7 days attendance
    last_week = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        total = Attendance.objects.filter(date=date).count()
        present = Attendance.objects.filter(date=date, status='P').count()
        last_week.append({
            'date': date,
            'total': total,
            'present': present,
            'percentage': (present / total * 100) if total > 0 else 0
        })
    
    context = {
        'total_students': total_students,
        'today_attendance': today_attendance,
        'present_today': present_today,
        'absent_today': absent_today,
        'late_today': late_today,
        'last_week': last_week,
    }
    return render(request, 'students/dashboard.html', context)

# Student Management
@login_required
def register_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.name} registered successfully!')
            return redirect('student_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm()
    
    return render(request, 'students/register_student.html', {'form': form})

@login_required
def student_list(request):
    students = Student.objects.filter(is_active=True)
    return render(request, 'students/student_list.html', {'students': students})

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    attendances = Attendance.objects.filter(student=student)[:30]
    
    # Calculate attendance percentage
    total_days = attendances.count()
    present_days = attendances.filter(status='P').count()
    late_days = attendances.filter(status='L').count()
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    context = {
        'student': student,
        'attendances': attendances,
        'total_days': total_days,
        'present_days': present_days,
        'late_days': late_days,
        'attendance_percentage': attendance_percentage,
    }
    return render(request, 'students/student_detail.html', context)

# Attendance Management
@login_required
def mark_attendance(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        if not date:
            messages.error(request, 'Please select a date.')
            return redirect('mark_attendance')
        
        # Check if attendance already marked for this date
        if Attendance.objects.filter(date=date).exists():
            messages.warning(request, f'Attendance for {date} has already been marked. You can edit it.')
        
        students = Student.objects.filter(is_active=True)
        
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            remarks = request.POST.get(f'remarks_{student.id}', '')
            
            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=date,
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'marked_by': request.user
                    }
                )
        
        messages.success(request, f'Attendance for {date} saved successfully!')
        return redirect('attendance_report')
    
    students = Student.objects.filter(is_active=True)
    form = AttendanceForm(students=students)
    today = timezone.now().date()
    
    return render(request, 'students/mark_attendance.html', {
        'form': form,
        'students': students,
        'today': today
    })

# Reports
@login_required
def attendance_report(request):
    form = DateRangeForm()
    report_data = []
    summary = {}
    
    if request.method == 'GET' and request.GET.get('start_date'):
        form = DateRangeForm(request.GET)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Get all students with their attendance for the date range
            students = Student.objects.filter(is_active=True)
            
            for student in students:
                attendances = Attendance.objects.filter(
                    student=student,
                    date__range=[start_date, end_date]
                ).order_by('date')
                
                total = attendances.count()
                present = attendances.filter(status='P').count()
                absent = attendances.filter(status='A').count()
                late = attendances.filter(status='L').count()
                percentage = (present / total * 100) if total > 0 else 0
                
                report_data.append({
                    'student': student,
                    'total': total,
                    'present': present,
                    'absent': absent,
                    'late': late,
                    'percentage': round(percentage, 2),
                    'attendances': attendances
                })
            
            summary = {
                'start_date': start_date,
                'end_date': end_date,
                'total_students': students.count(),
                'total_records': sum(r['total'] for r in report_data),
                'overall_present': sum(r['present'] for r in report_data),
                'overall_absent': sum(r['absent'] for r in report_data),
                'overall_late': sum(r['late'] for r in report_data),
            }
    
    return render(request, 'students/attendance_report.html', {
        'form': form,
        'report_data': report_data,
        'summary': summary
    })
