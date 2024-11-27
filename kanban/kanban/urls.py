from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from tasks.views import kanban_board
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('add/', views.add_task, name='add_task'),
    path('<int:task_id>', views.view_task, name='view_task'),
    path('<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('archive/', views.archive, name='archive'),
    path('<int:task_id>/archive/', views.archive_task, name='archive_task'),
    path('task/<int:task_id>/unarchive/', views.unarchive_task, name='unarchive_task'),
    path('', kanban_board, name='kanban_board')
]