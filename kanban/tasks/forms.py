from django import forms
from django.contrib.auth.models import Group
from .models import Task, Comment

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['archived', 'created_at', 'column']
        fields = [
            'country', 'sector', 'status',
            'priority', 'source', 'coverages', 'assigned_employee', 'file'
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
        # Capture the current task instance if available
        task = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        # Initialize the `assigned_employee` field
        self.fields['assigned_employee'] = forms.ModelChoiceField(
            queryset=None,  # Empty queryset by default
            required=False,
            label="Assigned Employee"
        )

        # Exclude admins from selection
        all_employees = Task._meta.get_field('assigned_employee').related_model.objects.filter(is_superuser=False)

        if task:
            # Editing mode: filter employees based on the task's column
            if task.column in ["expertise", "notificeren"]:
                expertise_group = Group.objects.get(name="Team Expertise")
                self.fields['assigned_employee'].queryset = expertise_group.user_set.filter(pk__in=all_employees)
            elif task.column == "contentbeheer":
                contentbeheer_group = Group.objects.get(name="Team Contentbeheer")
                self.fields['assigned_employee'].queryset = contentbeheer_group.user_set.filter(pk__in=all_employees)
        else:
            # Creating mode: default to Team Expertise
            expertise_group = Group.objects.get(name="Team Expertise")
            self.fields['assigned_employee'].queryset = expertise_group.user_set.filter(pk__in=all_employees)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Add your comment here...',
                'rows': 3
            }),
        }
