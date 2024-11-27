from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Task, TaskStatus, ColumnStatus
from .forms import TaskForm

@login_required
def kanban_board(request):
    expertise_tasks = Task.objects.filter(column=ColumnStatus.EXPERTISE, archived=False)
    contentbeheer_tasks = Task.objects.filter(column=ColumnStatus.CONTENTBEHEER, archived=False)
    notificeren_tasks = Task.objects.filter(column=ColumnStatus.NOTIFICEREN, archived=False)
    
    context = {
        'expertise_tasks': expertise_tasks,
        'contentbeheer_tasks': contentbeheer_tasks,
        'notificeren_tasks': notificeren_tasks,
    }
    return render(request, 'kanban_board.html', context)

@login_required
def view_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'view_task.html', {'task': task})

def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_employee = None
            task.save()
            return redirect('kanban_board')
        else:
            print(form.errors)  # Debugging: Print form errors to check validation issues
    else:
        form = TaskForm()
    return render(request, 'task_form.html', {'form': form})

def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            if task.column_status != request.POST.get('column'):
                task.assigned_employee = None  # Reset assigned employee on column change
            task.save()
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
    task.save()
    return redirect('kanban_board')

def unarchive_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.archived = False
    task.save()
    return redirect('kanban_board')