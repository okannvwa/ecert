from django.contrib import admin
from .models import Task

# Maak je Task model zichtbaar in de admin interface
admin.site.register(Task)