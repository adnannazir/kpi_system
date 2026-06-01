from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import Employee, Department, KPI, KPICategory, EmployeeKPI, PerformanceReview, Goal
from .forms import (
    EmployeeForm, DepartmentForm, KPIForm, KPICategoryForm,
    EmployeeKPIForm, EmployeeKPIUpdateForm, PerformanceReviewForm, GoalForm
)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    total_employees = Employee.objects.filter(status='active').count()
    total_departments = Department.objects.count()
    total_kpis = KPI.objects.filter(is_active=True).count()
    
    reviews_this_month = PerformanceReview.objects.filter(
        review_date__month=date.today().month,
        review_date__year=date.today().year
    ).count()

    # KPI status breakdown
    all_ekpis = EmployeeKPI.objects.all()
    kpi_stats = {
        'exceeded': sum(1 for e in all_ekpis if e.status == 'exceeded'),
        'on_track': sum(1 for e in all_ekpis if e.status == 'on_track'),
        'at_risk': sum(1 for e in all_ekpis if e.status == 'at_risk'),
        'below_target': sum(1 for e in all_ekpis if e.status == 'below_target'),
        'pending': sum(1 for e in all_ekpis if e.status == 'pending'),
    }

    # Recent reviews
    recent_reviews = PerformanceReview.objects.select_related('employee', 'reviewer').order_by('-review_date')[:5]

    # Top performers (employees with highest average review scores)
    employees_with_reviews = []
    for emp in Employee.objects.filter(status='active'):
        if emp.avg_score:
            employees_with_reviews.append(emp)
    top_performers = sorted(employees_with_reviews, key=lambda e: e.avg_score, reverse=True)[:5]

    # Department performance
    departments = Department.objects.annotate(emp_count=Count('employee'))

    # Goals overview
    goals_summary = {
        'total': Goal.objects.count(),
        'completed': Goal.objects.filter(status='completed').count(),
        'in_progress': Goal.objects.filter(status='in_progress').count(),
        'overdue': Goal.objects.filter(due_date__lt=date.today()).exclude(status__in=['completed', 'cancelled']).count(),
    }

    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_kpis': total_kpis,
        'reviews_this_month': reviews_this_month,
        'kpi_stats': kpi_stats,
        'recent_reviews': recent_reviews,
        'top_performers': top_performers,
        'departments': departments,
        'goals_summary': goals_summary,
    }
    return render(request, 'dashboard/index.html', context)


# --- Employee Views ---
@login_required
def employee_list(request):
    q = request.GET.get('q', '')
    dept = request.GET.get('dept', '')
    status = request.GET.get('status', '')
    employees = Employee.objects.select_related('department', 'manager').all()
    if q:
        employees = employees.filter(Q(full_name__icontains=q) | Q(email__icontains=q) | Q(employee_id__icontains=q))
    if dept:
        employees = employees.filter(department_id=dept)
    if status:
        employees = employees.filter(status=status)
    departments = Department.objects.all()
    return render(request, 'employees/list.html', {
        'employees': employees, 'departments': departments,
        'q': q, 'dept': dept, 'status': status
    })


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    reviews = employee.performancereview_set.order_by('-review_date')[:5]
    goals = employee.goal_set.order_by('-created_at')[:5]
    kpis = employee.employeekpi_set.select_related('kpi').order_by('-period_end')[:10]
    return render(request, 'employees/detail.html', {
        'employee': employee, 'reviews': reviews, 'goals': goals, 'kpis': kpis
    })


@login_required
def employee_create(request):
    form = EmployeeForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Employee created successfully.')
        return redirect('employee_list')
    return render(request, 'employees/form.html', {'form': form, 'title': 'Add Employee'})


@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None, request.FILES or None, instance=employee)
    if form.is_valid():
        form.save()
        messages.success(request, 'Employee updated successfully.')
        return redirect('employee_detail', pk=pk)
    return render(request, 'employees/form.html', {'form': form, 'title': 'Edit Employee', 'employee': employee})


@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted.')
        return redirect('employee_list')
    return render(request, 'employees/confirm_delete.html', {'employee': employee})


# --- Department Views ---
@login_required
def department_list(request):
    departments = Department.objects.annotate(emp_count=Count('employee'))
    return render(request, 'departments/list.html', {'departments': departments})


@login_required
def department_create(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Department created.')
        return redirect('department_list')
    return render(request, 'departments/form.html', {'form': form, 'title': 'Add Department'})


@login_required
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=dept)
    if form.is_valid():
        form.save()
        messages.success(request, 'Department updated.')
        return redirect('department_list')
    return render(request, 'departments/form.html', {'form': form, 'title': 'Edit Department', 'dept': dept})


@login_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.delete()
        messages.success(request, 'Department deleted.')
        return redirect('department_list')
    return render(request, 'departments/confirm_delete.html', {'dept': dept})


# --- KPI Views ---
@login_required
def kpi_list(request):
    kpis = KPI.objects.select_related('category').all()
    categories = KPICategory.objects.all()
    return render(request, 'kpis/list.html', {'kpis': kpis, 'categories': categories})


@login_required
def kpi_create(request):
    form = KPIForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'KPI created.')
        return redirect('kpi_list')
    return render(request, 'kpis/form.html', {'form': form, 'title': 'Create KPI'})


@login_required
def kpi_edit(request, pk):
    kpi = get_object_or_404(KPI, pk=pk)
    form = KPIForm(request.POST or None, instance=kpi)
    if form.is_valid():
        form.save()
        messages.success(request, 'KPI updated.')
        return redirect('kpi_list')
    return render(request, 'kpis/form.html', {'form': form, 'title': 'Edit KPI', 'kpi': kpi})


@login_required
def kpi_delete(request, pk):
    kpi = get_object_or_404(KPI, pk=pk)
    if request.method == 'POST':
        kpi.delete()
        messages.success(request, 'KPI deleted.')
        return redirect('kpi_list')
    return render(request, 'kpis/confirm_delete.html', {'kpi': kpi})


# --- Employee KPI Tracking ---
@login_required
def ekpi_list(request):
    ekpis = EmployeeKPI.objects.select_related('employee', 'kpi').order_by('-period_end')
    return render(request, 'ekpis/list.html', {'ekpis': ekpis})


@login_required
def ekpi_create(request):
    form = EmployeeKPIForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'KPI assigned to employee.')
        return redirect('ekpi_list')
    return render(request, 'ekpis/form.html', {'form': form, 'title': 'Assign KPI'})


@login_required
def ekpi_update(request, pk):
    ekpi = get_object_or_404(EmployeeKPI, pk=pk)
    form = EmployeeKPIUpdateForm(request.POST or None, instance=ekpi)
    if form.is_valid():
        form.save()
        messages.success(request, 'KPI progress updated.')
        return redirect('ekpi_list')
    return render(request, 'ekpis/update_form.html', {'form': form, 'ekpi': ekpi})


# --- Performance Review Views ---
@login_required
def review_list(request):
    reviews = PerformanceReview.objects.select_related('employee', 'reviewer').order_by('-review_date')
    return render(request, 'reviews/list.html', {'reviews': reviews})


@login_required
def review_create(request):
    form = PerformanceReviewForm(request.POST or None)
    if form.is_valid():
        review = form.save(commit=False)
        review.reviewer = request.user
        review.save()
        messages.success(request, 'Performance review submitted.')
        return redirect('review_list')
    return render(request, 'reviews/form.html', {'form': form, 'title': 'New Performance Review'})


@login_required
def review_detail(request, pk):
    review = get_object_or_404(PerformanceReview, pk=pk)
    return render(request, 'reviews/detail.html', {'review': review})


@login_required
def review_edit(request, pk):
    review = get_object_or_404(PerformanceReview, pk=pk)
    form = PerformanceReviewForm(request.POST or None, instance=review)
    if form.is_valid():
        form.save()
        messages.success(request, 'Review updated.')
        return redirect('review_detail', pk=pk)
    return render(request, 'reviews/form.html', {'form': form, 'title': 'Edit Review', 'review': review})


@login_required
def review_delete(request, pk):
    review = get_object_or_404(PerformanceReview, pk=pk)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted.')
        return redirect('review_list')
    return render(request, 'reviews/confirm_delete.html', {'review': review})


# --- Goal Views ---
@login_required
def goal_list(request):
    goals = Goal.objects.select_related('employee', 'created_by').order_by('-created_at')
    return render(request, 'goals/list.html', {'goals': goals})


@login_required
def goal_create(request):
    form = GoalForm(request.POST or None)
    if form.is_valid():
        goal = form.save(commit=False)
        goal.created_by = request.user
        goal.save()
        messages.success(request, 'Goal created.')
        return redirect('goal_list')
    return render(request, 'goals/form.html', {'form': form, 'title': 'Create Goal'})


@login_required
def goal_edit(request, pk):
    goal = get_object_or_404(Goal, pk=pk)
    form = GoalForm(request.POST or None, instance=goal)
    if form.is_valid():
        form.save()
        messages.success(request, 'Goal updated.')
        return redirect('goal_list')
    return render(request, 'goals/form.html', {'form': form, 'title': 'Edit Goal', 'goal': goal})


@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(Goal, pk=pk)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted.')
        return redirect('goal_list')
    return render(request, 'goals/confirm_delete.html', {'goal': goal})


# --- Analytics ---
@login_required
def analytics(request):
    # Department performance averages
    dept_data = []
    for dept in Department.objects.all():
        emp_ids = dept.employee_set.values_list('id', flat=True)
        reviews = PerformanceReview.objects.filter(employee_id__in=emp_ids)
        if reviews.exists():
            avg = reviews.aggregate(
                q=Avg('quality_score'), p=Avg('productivity_score'),
                t=Avg('teamwork_score'), c=Avg('communication_score'),
                i=Avg('initiative_score')
            )
            overall = round(sum([avg['q'] or 0, avg['p'] or 0, avg['t'] or 0,
                                  avg['c'] or 0, avg['i'] or 0]) / 5, 2)
            dept_data.append({'name': dept.name, 'score': overall, 'count': reviews.count()})

    # Monthly review trend (last 6 months)
    monthly_trend = []
    for i in range(5, -1, -1):
        d = date.today().replace(day=1) - timedelta(days=i * 30)
        count = PerformanceReview.objects.filter(
            review_date__year=d.year, review_date__month=d.month
        ).count()
        monthly_trend.append({'month': d.strftime('%b %Y'), 'count': count})

    # KPI achievement rates by category
    category_kpi = []
    for cat in KPICategory.objects.all():
        ekpis = EmployeeKPI.objects.filter(kpi__category=cat)
        achieved = sum(1 for e in ekpis if e.achievement_percentage and e.achievement_percentage >= 100)
        total = ekpis.count()
        category_kpi.append({
            'name': cat.name,
            'achieved': achieved,
            'total': total,
            'rate': round((achieved / total * 100), 1) if total > 0 else 0
        })

    context = {
        'dept_data': json.dumps(dept_data),
        'monthly_trend': json.dumps(monthly_trend),
        'category_kpi': json.dumps(category_kpi),
        'dept_data_raw': dept_data,
        'category_kpi_raw': category_kpi,
    }
    return render(request, 'analytics/index.html', context)
