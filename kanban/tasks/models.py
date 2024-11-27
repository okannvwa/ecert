from django.db import models
from django.contrib.auth.models import User

# Possible statuses of the task
class TaskStatus(models.TextChoices):
    TODO = 'todo', 'To Do'
    DOING = 'doing', 'Doing'

class ColumnStatus(models.TextChoices):
    EXPERTISE = 'expertise', 'Expertise'
    CONTENTBEHEER = 'contentbeheer', 'Contentbeheer'
    NOTIFICEREN = 'notificeren', 'Notificeren'

class SectorChoices(models.TextChoices):
    AGRICULTURE = 'agriculture', 'Agriculture'
    TECHNOLOGY = 'technology', 'Technology'
    FINANCE = 'finance', 'Finance'
    # Add more sectors as needed

class Task(models.Model):
    country = models.CharField(max_length=100, default="Unknown")
    sector = models.CharField(
        max_length=20,
        choices=SectorChoices.choices,
        blank=True
    )
    status = models.CharField(
        max_length=10,
        choices=TaskStatus.choices,
        default=TaskStatus.TODO
    )
    column = models.CharField(
        max_length=20,
        choices=ColumnStatus.choices,
        default=ColumnStatus.EXPERTISE
    )
    assigned_employee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    source = models.TextField(blank=True)
    coverages = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.country} - {self.sector}"
