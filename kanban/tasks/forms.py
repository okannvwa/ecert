from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['archived', 'created_at', 'column']
        fields = [
            'country', 'sector', 'status',
            'priority', 'source', 'coverages', 'assigned_employee'
        ]
        widgets = {
            'source': forms.Textarea(attrs={
                'placeholder': 'Optional: Can be filled in later.',
                'rows': 3
            }),
            'coverages': forms.Textarea(attrs={
                'placeholder': 'Optional: Can be filled in later.',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].required = True
        self.fields['sector'].required = True
        if self.instance.pk:  # Task exists (editing mode)
            self.fields['assigned_employee'] = forms.ModelChoiceField(
                queryset=Task._meta.get_field('assigned_employee').related_model.objects.all(),
                required=False,
                label="Assigned Employee"
            )
