from django import forms
from django.contrib.auth.models import Group
from .models import Task, Comment

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['archived', 'created_at', 'column', 'date_archived']
        fields = [
            'description',  'status','priority','sector', 'assigned_employee', 'country',
             'source', 'coverages',  'file', 'notes'
        ]
        labels = {
            'description': 'Omschrijving',
            'country': 'Land',
            'sector': 'Sector',
            'status': 'Status',
            'priority': 'Prioriteit',
            'source': 'Bron',
            'coverages': 'Dekkingscode(s)',
            'assigned_employee': 'Medewerker',
            'file': 'Bestand toevoegen',
            'notes': 'Notities',
        }
        widgets = {
            'description': forms.TextInput(attrs={
                'placeholder': 'Korte beschrijving van de taak.',
                'class': 'form-control w-100',
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control w-50',
            }),
            'sector': forms.Select(attrs={
                'class': 'form-control w-50 rounded-pill',
            }),
            'status': forms.Select(attrs={
                'class': 'form-control w-50 rounded-pill',
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control w-50 rounded-pill',
            }),
            'source': forms.Textarea(attrs={
                'placeholder': 'URL, bestandlocatie of elders',
                'rows': 1,
                'class': 'form-control w-50',
            }),
            'coverages': forms.Textarea(attrs={
                'placeholder': 'Code(s)',
                'rows': 1,
                'class': 'form-control w-50',
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Beschrijf hier de aanvullende informatie...',
                'rows': 5,
                'class': 'form-control w-100',
            }),
            'file': forms.FileInput(attrs={
                'class': 'w-100',
            }),
        }

    def __init__(self, *args, **kwargs):
        task = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        # Initialize the `assigned_employee` field
        self.fields['assigned_employee'] = forms.ModelChoiceField(
            queryset=None,  # Empty queryset by default
            required=False,
            label="Medewerker",
            widget=forms.Select(attrs={
                'class': 'form-control w-50 rounded-pill',
            })
        )

        # Exclude admins from selection
        all_employees = Task._meta.get_field('assigned_employee').related_model.objects.filter(is_superuser=False)

        if task:
            # Editing mode: filter employees based on the task's column
            if task.column in ["expertise", "notificeren"]:
                expertise_group = Group.objects.get(name="Expertise")
                self.fields['assigned_employee'].queryset = expertise_group.user_set.filter(pk__in=all_employees)
            elif task.column == "contentbeheer":
                contentbeheer_group = Group.objects.get(name="Contentbeheer")
                self.fields['assigned_employee'].queryset = contentbeheer_group.user_set.filter(pk__in=all_employees)
        else:
            # Creating mode: default to Team Expertise
            expertise_group = Group.objects.get(name="Expertise")
            self.fields['assigned_employee'].queryset = expertise_group.user_set.filter(pk__in=all_employees)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Voeg uw opmerking hier toe...',
                'rows': 3
            }),
        }
