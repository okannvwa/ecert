from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Task, TaskStatus, ColumnStatus, PriorityChoices, Comment
from .forms import TaskForm, CommentForm
from django.db.models import Case, When, Value, IntegerField
from .utils import has_permission_for_task

@login_required
def kanban_board(request):
    # Get filter options from GET parameters
    sector_filter = request.GET.get('sector')
    my_tasks_only = request.GET.get('my_tasks', False)

    # Base query for tasks (exclude archived)
    base_query = Task.objects.filter(archived=False)

    # Apply filters
    if sector_filter:
        base_query = base_query.filter(sector=sector_filter)
    if my_tasks_only == 'true':
        base_query = base_query.filter(assigned_employee=request.user)

    # Custom priority ordering (High > Medium > Low)
    priority_order = Case(
        When(priority=PriorityChoices.HIGH, then=Value(1)),
        When(priority=PriorityChoices.MEDIUM, then=Value(2)),
        When(priority=PriorityChoices.LOW, then=Value(3)),
        output_field=IntegerField()
    )

    # Order tasks by priority
    ordered_tasks = base_query.annotate(priority_order=priority_order).order_by('priority_order')

    # Split tasks into columns
    expertise_tasks = ordered_tasks.filter(column=ColumnStatus.EXPERTISE)
    contentbeheer_tasks = ordered_tasks.filter(column=ColumnStatus.CONTENTBEHEER)
    notificeren_tasks = ordered_tasks.filter(column=ColumnStatus.NOTIFICEREN)

    # Get distinct sector options for dropdown
    sector_choices = Task.objects.values_list('sector', flat=True).distinct()

    can_add_task = request.user.is_superuser or request.user.groups.filter(name="Team Expertise").exists()

    context = {
        'expertise_tasks': expertise_tasks,
        'contentbeheer_tasks': contentbeheer_tasks,
        'notificeren_tasks': notificeren_tasks,
        'sector_choices': sector_choices,
        'selected_sector': sector_filter,
        'my_tasks_only': my_tasks_only,
        'can_add_task': can_add_task,
    }
    return render(request, 'kanban_board.html', context)



@login_required
def view_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    comments = task.comments.all().order_by('-created_at')

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return redirect('view_task', task_id=task.id)
    else:
        comment_form = CommentForm()

    user_has_permission = has_permission_for_task(request.user, task)

    context = {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
        'user_has_permission': user_has_permission, 
    }
    return render(request, 'view_task.html', context)

def is_team_expertise(user):
    return user.groups.filter(name="Team Expertise").exists() or user.is_superuser

@user_passes_test(is_team_expertise)
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.column = ColumnStatus.EXPERTISE # Tasks always start in Expertise
            task.save()
            return redirect('kanban_board')
    else:
        form = TaskForm()
    return render(request, 'task_form.html', {'form': form})

def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if not has_permission_for_task(request.user, task):
        return HttpResponseForbidden("U heeft geen toegang om deze taak te bewerken.")
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save(commit=False)
            if updated_task.column != task.column:
                updated_task.assigned_employee = None  # Reset medewerker als de kolom verandert
            updated_task.save()
            return redirect('kanban_board')
    else:
        form = TaskForm(instance=task)
    return render(request, 'task_form.html', {'form': form, 'task': task})

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('archive')

@login_required
def archive(request):
    archived_tasks = Task.objects.filter(archived=True)
    return render(request, 'archive.html', {'archived_tasks': archived_tasks})

def archive_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.archived = True
    task.status = TaskStatus.TODO
    task.save()
    return redirect('kanban_board')

def unarchive_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.archived = False
    task.save()
    return redirect('kanban_board')

def move_task(request, task_id, direction):
    task = get_object_or_404(Task, id=task_id)
    if not has_permission_for_task(request.user, task):
        return HttpResponseForbidden("U heeft geen toegang om deze taak te verplaatsen.")

    if direction == 'next':
        if task.column == ColumnStatus.EXPERTISE:
            task.column = ColumnStatus.CONTENTBEHEER
        elif task.column == ColumnStatus.CONTENTBEHEER:
            task.column = ColumnStatus.NOTIFICEREN
    elif direction == 'previous':
        if task.column == ColumnStatus.CONTENTBEHEER:
            task.column = ColumnStatus.EXPERTISE
        elif task.column == ColumnStatus.NOTIFICEREN:
            task.column = ColumnStatus.CONTENTBEHEER

    # Reset the assigned employee when moving between columns
    task.assigned_employee = None
    task.save()

    # Redirect to the kanban board after the move
    return redirect('kanban_board')