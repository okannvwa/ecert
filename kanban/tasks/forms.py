from django import forms
from .models import Task, ColumnStatus

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['archived', 'created_at']
        fields = ['country', 'sector', 'status', 'assigned_employee', 'source', 'coverages']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Only for new tasks
            self.fields['source'].required = False
            self.fields['coverages'].required = False

