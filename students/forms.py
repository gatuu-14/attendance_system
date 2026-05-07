from django import forms
from .models import Student, Attendance
from datetime import date

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['register_number', 'name', 'date_of_birth', 'gender', 
                 'email', 'phone', 'address']
        widgets = {
            'register_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2024001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'student@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
        }

class AttendanceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        students = kwargs.pop('students', None)
        super().__init__(*args, **kwargs)
        if students:
            for student in students:
                self.fields[f'status_{student.id}'] = forms.ChoiceField(
                    choices=Attendance.STATUS_CHOICES,
                    widget=forms.Select(attrs={'class': 'form-control status-select'}),
                    label=student.name,
                    initial='P'
                )
                self.fields[f'remarks_{student.id}'] = forms.CharField(
                    required=False,
                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional remarks'}),
                    label=''
                )

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )