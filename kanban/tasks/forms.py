from django import forms
from .models import Task, TaskStatus

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status']
        widgets = {
            'status': forms.Select(choices=TaskStatus.choices)
        }