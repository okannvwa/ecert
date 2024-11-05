from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Task, TaskStatus
from .forms import TaskForm

@login_required
def kanban_board(request):
    # Haal de taken op per status
    expertise_tasks = Task.objects.filter(status=TaskStatus.EXPERTISE)
    contentbeheer_tasks = Task.objects.filter(status=TaskStatus.CONTENTBEHEER)
    notificeren_tasks = Task.objects.filter(status=TaskStatus.NOTIFICEREN)

    context = {
        'expertise_tasks': expertise_tasks,
        'contentbeheer_tasks': contentbeheer_tasks,
        'notificeren_tasks': notificeren_tasks
    }

    return render(request, 'kanban_board.html', context)

@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kanban_board')
    else:
        form = TaskForm()
    return render(request, 'add_task.html', {'form': form})

@login_required
def view_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'view_task.html', {'task': task})

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('kanban_board')
    else:
        form = TaskForm(instance=task)
    return render(request, 'edit_task.html', {'form': form, 'task': task})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        return redirect('kanban_board')
    return render(request, 'delete_task.html', {'task': task})

