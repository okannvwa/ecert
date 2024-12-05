from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.http import HttpRequest
from .models import Task, ColumnStatus, TaskStatus, SectorChoices, PriorityChoices
from .views import (
    add_task, edit_task, archive_task, unarchive_task, delete_task, move_task, kanban_board
)
from .forms import TaskForm
from rest_framework.test import APIClient
import json


class TaskFunctionTests(TestCase):
    def setUp(self):
        # Create groups and users
        self.team_expertise = Group.objects.create(name="Team Expertise")
        self.expertise_user = User.objects.create_user(username="expert_user", password="testpass")
        self.expertise_user.groups.add(self.team_expertise)

        # Create tasks
        self.task = Task.objects.create(
            country="Netherlands",
            sector=SectorChoices.GROENTEENFRUIT,
            status=TaskStatus.TODO,
            column=ColumnStatus.EXPERTISE,
            assigned_employee=self.expertise_user,
            priority=PriorityChoices.HIGH,
            source="Source example",
            coverages="Coverage example",
            archived=False
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.expertise_user)
        self.factory = RequestFactory()

    def test_create_task_function(self):
        """UT1: Test task creation via add_task view."""
        form_data = {
            "country": "Belgium",
            "sector": SectorChoices.GROENTEENFRUIT,  # Use a valid sector choice
            "status": TaskStatus.TODO,
            "priority": PriorityChoices.MEDIUM,
            "source": "API Source",
            "coverages": "API Coverage",
        } 
        request = self.factory.post(reverse('add_task'), data=form_data)
        request.user = self.expertise_user
        response = add_task(request)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(response.status_code, 302)  # Redirect to kanban_board

    def test_edit_task_function(self):
        """UT2: Test task editing via edit_task view."""
        form_data = {
            "country": "Germany",
            "sector": SectorChoices.ZAAIZADEN,
            "status": self.task.status,
            "priority": self.task.priority,
            "source": self.task.source,
            "coverages": self.task.coverages,
        }
        request = self.factory.post(reverse('edit_task', args=[self.task.id]), data=form_data)
        request.user = self.expertise_user
        response = edit_task(request, self.task.id)
        self.assertEqual(response.status_code, 302)  # Redirect to kanban_board
        self.task.refresh_from_db()
        self.assertEqual(self.task.country, "Germany")

    def test_archive_task_function(self):
        """UT3: Test archiving a task via archive_task view."""
        request = self.factory.get(reverse('archive_task', args=[self.task.id]))
        request.user = self.expertise_user
        response = archive_task(request, self.task.id)
        self.assertEqual(response.status_code, 302)  # Redirect to kanban_board
        self.task.refresh_from_db()
        self.assertTrue(self.task.archived)

    def test_unarchive_task_function(self):
        """UT4: Test unarchiving a task via unarchive_task view."""
        self.task.archived = True
        self.task.save()
        request = self.factory.get(reverse('unarchive_task', args=[self.task.id]))
        request.user = self.expertise_user
        response = unarchive_task(request, self.task.id)
        self.assertEqual(response.status_code, 302)  # Redirect to kanban_board
        self.task.refresh_from_db()
        self.assertFalse(self.task.archived)

    def test_delete_task_function(self):
        """UT5: Test deleting a task via delete_task view."""
        task_id = self.task.id
        request = self.factory.get(reverse('delete_task', args=[task_id]))
        request.user = self.expertise_user
        response = delete_task(request, task_id)
        self.assertEqual(response.status_code, 302)  # Redirect to archive
        self.assertFalse(Task.objects.filter(id=task_id).exists())


class TaskComponentTests(TestCase):
    def setUp(self):
        self.team_expertise = Group.objects.create(name="Team Expertise")
        self.expertise_user = User.objects.create_user(username="expert_user", password="testpass")
        self.expertise_user.groups.add(self.team_expertise)

        # Log in using the default client
        self.client.login(username="expert_user", password="testpass")

        # Create tasks (unarchived and archived)
        self.unarchived_task = Task.objects.create(
            country="Netherlands",
            sector=SectorChoices.ZAAIZADEN,
            status=TaskStatus.TODO,
            column=ColumnStatus.EXPERTISE,
            assigned_employee=self.expertise_user,
            priority=PriorityChoices.HIGH,
            source="Source example",
            coverages="Coverage example",
            archived=False,
        )
        self.archived_task = Task.objects.create(
            country="Germany",
            sector=SectorChoices.DIVERS,
            status=TaskStatus.WAITING,
            column=ColumnStatus.EXPERTISE,
            assigned_employee=self.expertise_user,
            priority=PriorityChoices.LOW,
            source="Source 2",
            coverages="Coverage 2",
            archived=True,
        )

    def test_get_archived_tasks(self):
        """CT3: Verify all archived tasks are displayed in the rendered HTML."""
        # Send a GET request to the archived tasks page (assuming the URL name is 'archive')
        response = self.client.get(reverse('archive'))

        # Assert the response status is OK (200)
        self.assertEqual(response.status_code, 200)

        # Decode the response content to check the HTML content
        content = response.content.decode()

        # Verify the archived task is present in the HTML
        self.assertIn("<strong>Land:</strong> Germany", content)
        self.assertIn("<strong>Sector:</strong> Diverse Producten", content)

        # Verify the unarchived task is NOT present in the HTML
        self.assertNotIn("<strong>Land:</strong> Netherlands", content)
        self.assertNotIn("<strong>Sector:</strong> Zaaizaden", content)


    def test_get_specific_task(self):
        """CT2: Verify a specific task is fetched via API."""
        response = self.client.get(reverse('view_task', args=[self.unarchived_task.id]))

        # Assert that the response status is 200 OK (indicating no redirect)
        self.assertEqual(response.status_code, 200)

        # Parse the response content (assuming it returns HTML content)
        content = response.content.decode()

        # Verify that the task details are present in the content
        self.assertIn(self.unarchived_task.country, content)
        self.assertIn(self.unarchived_task.sector, content)

        # Ensure the archived task is not present
        self.assertNotIn(self.archived_task.country, content)
        self.assertNotIn(self.archived_task.sector, content)

    def test_get_unarchived_tasks(self):
        """CT1: Verify all unarchived tasks are displayed in the rendered HTML."""
        response = self.client.get(reverse('kanban_board'))

        # Assert the response status is OK
        self.assertEqual(response.status_code, 200)

        # Decode the response content to check HTML
        content = response.content.decode()

        # Verify the unarchived task is present in the HTML
        self.assertIn("<strong>Land:</strong> Netherlands", content)
        self.assertIn("<strong>Sector:</strong> Zaaizaden", content)
        # Verify the archived task is NOT present in the HTML
        self.assertNotIn("<strong>Land:</strong> Germany", content)
        self.assertNotIn("<strong>Sector:</strong> Diverse Producten", content)