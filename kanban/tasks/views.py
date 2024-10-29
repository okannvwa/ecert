from django.shortcuts import render
from .models import Task, TaskStatus
from django.contrib.auth.decorators import login_required

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