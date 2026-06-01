from django.contrib import admin
from .models import Department, Employee, KPICategory, KPI, EmployeeKPI, PerformanceReview, Goal

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'employee_count']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'department', 'job_title', 'status']
    list_filter = ['department', 'status']
    search_fields = ['full_name', 'email', 'employee_id']

@admin.register(KPICategory)
class KPICategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']

@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'target_value', 'is_active']
    list_filter = ['category', 'is_active']

@admin.register(EmployeeKPI)
class EmployeeKPIAdmin(admin.ModelAdmin):
    list_display = ['employee', 'kpi', 'period_start', 'period_end', 'actual_value', 'target_value']

@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ['employee', 'reviewer', 'review_type', 'review_date', 'overall_score']

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'due_date', 'status', 'priority', 'progress']
    list_filter = ['status', 'priority']
