from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managed_departments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def employee_count(self):
        return self.employee_set.count()


class Employee(models.Model):
    EMPLOYMENT_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    job_title = models.CharField(max_length=100)
    hire_date = models.DateField()
    status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='active')
    manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='direct_reports'
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"

    @property
    def avg_score(self):
        reviews = self.performancereview_set.all()
        if reviews.exists():
            return round(sum(r.overall_score for r in reviews) / reviews.count(), 1)
        return None

    @property
    def latest_review(self):
        return self.performancereview_set.order_by('-review_date').first()


class KPICategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#696cff')  # hex color

    def __str__(self):
        return self.name


class KPI(models.Model):
    UNIT_CHOICES = [
        ('percentage', 'Percentage (%)'),
        ('number', 'Number'),
        ('currency', 'Currency'),
        ('rating', 'Rating (1-10)'),
        ('boolean', 'Yes/No'),
    ]
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(KPICategory, on_delete=models.SET_NULL, null=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='percentage')
    target_value = models.FloatField()
    weight = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(10.0)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class EmployeeKPI(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    target_value = models.FloatField()
    actual_value = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['employee', 'kpi', 'period_start', 'period_end']

    def __str__(self):
        return f"{self.employee} - {self.kpi}"

    @property
    def achievement_percentage(self):
        if self.actual_value is not None and self.target_value > 0:
            return round((self.actual_value / self.target_value) * 100, 1)
        return None

    @property
    def status(self):
        pct = self.achievement_percentage
        if pct is None:
            return 'pending'
        if pct >= 100:
            return 'exceeded'
        if pct >= 80:
            return 'on_track'
        if pct >= 60:
            return 'at_risk'
        return 'below_target'


class PerformanceReview(models.Model):
    REVIEW_TYPE = [
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
        ('probation', 'Probation'),
        ('mid_year', 'Mid-Year'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='conducted_reviews'
    )
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPE, default='quarterly')
    review_date = models.DateField()
    period_start = models.DateField()
    period_end = models.DateField()

    # Scoring areas (1-5 scale)
    quality_score = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    productivity_score = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    teamwork_score = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication_score = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    initiative_score = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    strengths = models.TextField(blank=True)
    improvements = models.TextField(blank=True)
    goals_next_period = models.TextField(blank=True)
    overall_comments = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.employee} on {self.review_date}"

    @property
    def overall_score(self):
        scores = [
            self.quality_score, self.productivity_score, self.teamwork_score,
            self.communication_score, self.initiative_score
        ]
        return round(sum(scores) / len(scores), 2)

    @property
    def overall_percentage(self):
        return round((self.overall_score / 5) * 100, 1)

    @property
    def rating_label(self):
        score = self.overall_score
        if score >= 4.5:
            return ('Outstanding', 'success')
        if score >= 3.5:
            return ('Exceeds Expectations', 'primary')
        if score >= 2.5:
            return ('Meets Expectations', 'warning')
        if score >= 1.5:
            return ('Needs Improvement', 'danger')
        return ('Unsatisfactory', 'dark')


class Goal(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.employee})"
