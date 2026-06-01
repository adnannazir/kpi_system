from django import forms
from django.contrib.auth.models import User
from .models import Employee, Department, KPI, KPICategory, EmployeeKPI, PerformanceReview, Goal


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_id', 'full_name', 'email', 'phone', 'department',
                  'job_title', 'hire_date', 'status', 'manager', 'avatar']
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'employee_id': forms.TextInput(attrs={'placeholder': 'e.g., EMP-001'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@company.com'}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'manager']


class KPIForm(forms.ModelForm):
    class Meta:
        model = KPI
        fields = ['name', 'description', 'category', 'unit', 'target_value', 'weight', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class KPICategoryForm(forms.ModelForm):
    class Meta:
        model = KPICategory
        fields = ['name', 'description', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


class EmployeeKPIForm(forms.ModelForm):
    class Meta:
        model = EmployeeKPI
        fields = ['employee', 'kpi', 'period_start', 'period_end', 'target_value', 'actual_value', 'notes']
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class EmployeeKPIUpdateForm(forms.ModelForm):
    class Meta:
        model = EmployeeKPI
        fields = ['actual_value', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class PerformanceReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = [
            'employee', 'review_type', 'review_date', 'period_start', 'period_end',
            'quality_score', 'productivity_score', 'teamwork_score',
            'communication_score', 'initiative_score',
            'strengths', 'improvements', 'goals_next_period', 'overall_comments'
        ]
        widgets = {
            'review_date': forms.DateInput(attrs={'type': 'date'}),
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
            'strengths': forms.Textarea(attrs={'rows': 3}),
            'improvements': forms.Textarea(attrs={'rows': 3}),
            'goals_next_period': forms.Textarea(attrs={'rows': 3}),
            'overall_comments': forms.Textarea(attrs={'rows': 3}),
            'quality_score': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 0.1}),
            'productivity_score': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 0.1}),
            'teamwork_score': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 0.1}),
            'communication_score': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 0.1}),
            'initiative_score': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 0.1}),
        }


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['employee', 'title', 'description', 'due_date', 'status', 'priority', 'progress']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }
