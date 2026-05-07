from django.contrib import admin
from .models import Student, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['register_number', 'name', 'email', 'phone', 'is_active']
    list_filter = ['gender', 'is_active']
    search_fields = ['name', 'register_number', 'email']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'marked_by']
    list_filter = ['status', 'date']
    search_fields = ['student__name']
