from django.db import models
from django.contrib.auth.models import User


# =========================================================
# INCIDENT MODEL
# =========================================================
class Incident(models.Model):

    STATUS_CHOICES = (
        ('NORMAL', 'Normal'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='incidents',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
# =====================================================
# EARLY WARNING MODEL
# =====================================================
class EarlyWarning(models.Model):

    LEVELS = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    )

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE
    )

    warning_level = models.CharField(
        max_length=20,
        choices=LEVELS
    )

    message = models.TextField()

    issued_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.warning_level


# =========================================================
# HAZARD IMAGE MODEL
# =========================================================
class HazardImage(models.Model):

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='hazards/')
    caption = models.CharField(max_length=255)

    def __str__(self):
        return self.caption


# =========================================================
# SENSOR DATA MODEL
# =========================================================
class SensorData(models.Model):

    location = models.CharField(max_length=100)

    water_level = models.FloatField()
    rainfall = models.FloatField()
    temperature = models.FloatField()

    severity = models.CharField(
        max_length=20,
        choices=(
            ('NORMAL', 'Normal'),
            ('WARNING', 'Warning'),
            ('CRITICAL', 'Critical'),
        )
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location} - {self.severity}"


# =========================================================
# HAZARD REPORT MODEL
# =========================================================
class HazardReport(models.Model):

    SEVERITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    location = models.CharField(
        max_length=255
    )

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES
    )

    reported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hazard_reports'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title