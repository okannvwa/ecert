from django import forms
from .models import Task, ColumnStatus

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['archived', 'created_at']  # Exclude archived and created_at fields
        fields = [
            'country', 'sector', 'status', 'column',
            'assigned_employee', 'source', 'coverages'
        ]
        widgets = {
            'source': forms.Textarea(attrs={'placeholder': 'Leave empty when creating a new task'}),
            'coverages': forms.Textarea(attrs={'placeholder': 'Leave empty when creating a new task'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # If it's a new task
            self.fields['source'].required = False
            self.fields['coverages'].required = False
