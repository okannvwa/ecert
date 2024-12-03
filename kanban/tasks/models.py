from django.db import models
from django.contrib.auth.models import User

class TaskStatus(models.TextChoices):
    TODO = 'Te Doen', 'Te Doen'
    DOING = 'Mee Bezig', 'Mee Bezig'
    WAITING = 'In Afwachting', 'In Afwachting'

class ColumnStatus(models.TextChoices):
    EXPERTISE = 'expertise', 'Expertise'
    CONTENTBEHEER = 'contentbeheer', 'Contentbeheer'
    NOTIFICEREN = 'notificeren', 'Notificeren'

class SectorChoices(models.TextChoices):
    AARDAPPELEN = 'Aardappelen', 'Aardappelen'
    BLOEMBOLLEN = 'Bloembollen', 'Bloembollen'
    DIVERS = 'Diverse Producten', 'Diverse Producten'
    GROENTEENFRUIT = 'Groente en Fruit', 'Groente en Fruit'
    PLANTUIEN = 'Plantuien', 'Plantuien'
    SIERTEELT = 'Sierteelt', 'Sierteelt'
    ZAAIZADEN = 'Zaaizaden', 'Zaaizaden'

class PriorityChoices(models.TextChoices):
    HIGH = 'Hoog', 'Hoog'
    MEDIUM = 'Gemiddeld', 'Gemiddeld'
    LOW = 'Laag', 'Laag'

class Task(models.Model):
    country = models.CharField(max_length=100, default="")
    sector = models.CharField(
        max_length=40,
        choices=SectorChoices.choices,
        default=SectorChoices.ZAAIZADEN
    )
    status = models.CharField(
        max_length=15,
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
    priority = models.CharField(
        max_length=10,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM
    )
    source = models.TextField(blank=True)
    coverages = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    file = models.FileField(upload_to='task_files/', blank=True, null=True)

    def __str__(self):
        return f"{self.country} - {self.sector} - {self.priority}"

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.created_at}"