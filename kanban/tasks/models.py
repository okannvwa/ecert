from django.db import models

# Mogelijke statussen van de taken
class TaskStatus(models.TextChoices):
    EXPERTISE = 'expertise', 'Expertise'
    CONTENTBEHEER = 'contentbeheer', 'Contentbeheer'
    NOTIFICEREN = 'notificeren', 'Notificeren'

# Model voor een Taak
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.EXPERTISE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title