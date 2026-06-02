from django.db import models

class Incident(models.Model):

    STATUS_CHOICES = (
        ('NORMAL', 'Normal'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class HazardImage(models.Model):

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(
        upload_to='hazards/'
    )

    caption = models.CharField(
        max_length=255
    )