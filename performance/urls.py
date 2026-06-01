from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Employees
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),

    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),

    # KPIs
    path('kpis/', views.kpi_list, name='kpi_list'),
    path('kpis/create/', views.kpi_create, name='kpi_create'),
    path('kpis/<int:pk>/edit/', views.kpi_edit, name='kpi_edit'),
    path('kpis/<int:pk>/delete/', views.kpi_delete, name='kpi_delete'),

    # Employee KPI Tracking
    path('kpi-tracking/', views.ekpi_list, name='ekpi_list'),
    path('kpi-tracking/assign/', views.ekpi_create, name='ekpi_create'),
    path('kpi-tracking/<int:pk>/update/', views.ekpi_update, name='ekpi_update'),

    # Performance Reviews
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/create/', views.review_create, name='review_create'),
    path('reviews/<int:pk>/', views.review_detail, name='review_detail'),
    path('reviews/<int:pk>/edit/', views.review_edit, name='review_edit'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),

    # Goals
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/create/', views.goal_create, name='goal_create'),
    path('goals/<int:pk>/edit/', views.goal_edit, name='goal_edit'),
    path('goals/<int:pk>/delete/', views.goal_delete, name='goal_delete'),

    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]
