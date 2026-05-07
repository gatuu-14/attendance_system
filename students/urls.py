from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Student Management
    path('students/register/', views.register_student, name='register_student'),
    path('students/list/', views.student_list, name='student_list'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    
    # Attendance
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    
    # Reports
    path('attendance/report/', views.attendance_report, name='attendance_report'),
]