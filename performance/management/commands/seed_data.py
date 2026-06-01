from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from performance.models import Department, Employee, KPICategory, KPI, EmployeeKPI, PerformanceReview, Goal
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@company.com', 'admin123')
            admin.first_name = 'Admin'
            admin.last_name = 'User'
            admin.save()

        admin = User.objects.get(username='admin')

        # Departments
        dept_names = ['Engineering', 'Sales', 'Marketing', 'Human Resources', 'Finance']
        departments = []
        for name in dept_names:
            d, _ = Department.objects.get_or_create(name=name, defaults={'description': f'{name} department', 'manager': admin})
            departments.append(d)

        # Employees
        emp_data = [
            ('EMP-001', 'Sarah Johnson', 'sarah@company.com', 'Software Engineer', 0),
            ('EMP-002', 'Michael Chen', 'michael@company.com', 'Senior Developer', 0),
            ('EMP-003', 'Emily Davis', 'emily@company.com', 'Sales Manager', 1),
            ('EMP-004', 'James Wilson', 'james@company.com', 'Account Executive', 1),
            ('EMP-005', 'Lisa Martinez', 'lisa@company.com', 'Marketing Specialist', 2),
            ('EMP-006', 'David Brown', 'david@company.com', 'HR Coordinator', 3),
            ('EMP-007', 'Jennifer Lee', 'jennifer@company.com', 'Financial Analyst', 4),
            ('EMP-008', 'Robert Taylor', 'robert@company.com', 'DevOps Engineer', 0),
            ('EMP-009', 'Amanda White', 'amanda@company.com', 'Content Strategist', 2),
            ('EMP-010', 'Chris Anderson', 'chris@company.com', 'Business Development', 1),
        ]

        employees = []
        for eid, name, email, title, dept_idx in emp_data:
            emp, _ = Employee.objects.get_or_create(
                employee_id=eid,
                defaults={
                    'full_name': name,
                    'email': email,
                    'job_title': title,
                    'department': departments[dept_idx],
                    'hire_date': date.today() - timedelta(days=random.randint(180, 1500)),
                    'status': 'active',
                    'phone': f'+1-555-{random.randint(1000,9999)}',
                }
            )
            employees.append(emp)

        # KPI Categories
        cat_data = [('Productivity', '#696cff'), ('Quality', '#71dd37'), ('Sales', '#ff3e1d'), ('Collaboration', '#03c3ec')]
        categories = []
        for name, color in cat_data:
            c, _ = KPICategory.objects.get_or_create(name=name, defaults={'color': color})
            categories.append(c)

        # KPIs
        kpi_data = [
            ('Code Review Completion Rate', categories[0], 'percentage', 90, 1.5),
            ('Bug Resolution Time (hours)', categories[1], 'number', 24, 1.2),
            ('Monthly Sales Target', categories[2], 'currency', 50000, 2.0),
            ('Customer Satisfaction Score', categories[1], 'rating', 8, 1.8),
            ('Team Meeting Attendance', categories[3], 'percentage', 95, 1.0),
            ('Sprint Velocity', categories[0], 'number', 40, 1.3),
            ('Lead Conversion Rate', categories[2], 'percentage', 25, 1.7),
            ('Documentation Coverage', categories[1], 'percentage', 80, 1.0),
        ]

        kpis = []
        for name, cat, unit, target, weight in kpi_data:
            k, _ = KPI.objects.get_or_create(name=name, defaults={'category': cat, 'unit': unit, 'target_value': target, 'weight': weight})
            kpis.append(k)

        # Assign KPIs to employees
        period_start = date.today().replace(day=1) - timedelta(days=30)
        period_end = date.today()

        for emp in employees[:6]:
            for kpi in random.sample(kpis, 3):
                actual = round(kpi.target_value * random.uniform(0.6, 1.3), 1)
                EmployeeKPI.objects.get_or_create(
                    employee=emp, kpi=kpi, period_start=period_start, period_end=period_end,
                    defaults={'target_value': kpi.target_value, 'actual_value': actual}
                )

        # Performance Reviews
        review_types = ['quarterly', 'annual', 'mid_year']
        rating_combos = [
            (4.5, 4.2, 4.8, 4.3, 4.6),
            (3.5, 3.8, 3.2, 4.0, 3.6),
            (4.8, 4.9, 4.7, 4.5, 4.8),
            (3.0, 2.8, 3.5, 3.2, 3.0),
            (4.2, 4.0, 4.5, 4.1, 4.3),
        ]

        for i, emp in enumerate(employees[:8]):
            scores = rating_combos[i % len(rating_combos)]
            review_date = date.today() - timedelta(days=random.randint(5, 60))
            PerformanceReview.objects.get_or_create(
                employee=emp,
                review_date=review_date,
                defaults={
                    'reviewer': admin,
                    'review_type': random.choice(review_types),
                    'period_start': review_date - timedelta(days=90),
                    'period_end': review_date,
                    'quality_score': scores[0],
                    'productivity_score': scores[1],
                    'teamwork_score': scores[2],
                    'communication_score': scores[3],
                    'initiative_score': scores[4],
                    'strengths': 'Demonstrates strong technical skills and takes ownership of tasks.',
                    'improvements': 'Could benefit from more proactive communication with stakeholders.',
                    'goals_next_period': 'Lead at least one cross-functional project and mentor a junior team member.',
                    'overall_comments': 'A valued team member who consistently delivers quality work.',
                }
            )

        # Goals
        goal_data = [
            ('Complete Q3 Feature Roadmap', 'in_progress', 'high', 65, 30),
            ('Achieve Sales Target of $150K', 'in_progress', 'critical', 78, 45),
            ('Improve Code Test Coverage to 85%', 'not_started', 'medium', 20, 60),
            ('Launch New Marketing Campaign', 'completed', 'high', 100, -10),
            ('Reduce Customer Churn by 15%', 'in_progress', 'critical', 45, 90),
            ('Complete HR Policy Update', 'not_started', 'low', 10, 120),
        ]

        for i, (title, status, priority, progress, days_offset) in enumerate(goal_data):
            emp = employees[i % len(employees)]
            Goal.objects.get_or_create(
                employee=emp, title=title,
                defaults={
                    'status': status, 'priority': priority, 'progress': progress,
                    'due_date': date.today() + timedelta(days=days_offset),
                    'created_by': admin,
                    'description': f'Goal to {title.lower()} within the designated timeline.',
                }
            )

        self.stdout.write(self.style.SUCCESS('✅ Sample data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('Login: admin / admin123'))
