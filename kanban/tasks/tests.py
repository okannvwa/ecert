from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.http import HttpRequest
from .models import Task, ColumnStatus, TaskStatus, SectorChoices, PriorityChoices
from .views import add_task, edit_task, archive_task, unarchive_task, delete_task, move_task, kanban_board
from .forms import TaskForm
from rest_framework.test import APIClient
import json
import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class TaskFunctionTests(TestCase):
    def setUp(self):
        """Sets up test data for Task function tests."""
        self.team_expertise = Group.objects.create(name="Team Expertise")
        self.expertise_user = User.objects.create_user(username="expert_user", password="testpass")
        self.expertise_user.groups.add(self.team_expertise)

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
            "sector": SectorChoices.GROENTEENFRUIT,
            "status": TaskStatus.TODO,
            "priority": PriorityChoices.MEDIUM,
            "source": "API Source",
            "coverages": "API Coverage",
        }
        request = self.factory.post(reverse('add_task'), data=form_data)
        request.user = self.expertise_user
        response = add_task(request)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(response.status_code, 302)

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
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.country, "Germany")

    def test_archive_task_function(self):
        """UT3: Test archiving a task via archive_task view."""
        request = self.factory.get(reverse('archive_task', args=[self.task.id]))
        request.user = self.expertise_user
        response = archive_task(request, self.task.id)
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertTrue(self.task.archived)

    def test_unarchive_task_function(self):
        """UT4: Test unarchiving a task via unarchive_task view."""
        self.task.archived = True
        self.task.save()
        request = self.factory.get(reverse('unarchive_task', args=[self.task.id]))
        request.user = self.expertise_user
        response = unarchive_task(request, self.task.id)
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertFalse(self.task.archived)

    def test_delete_task_function(self):
        """UT5: Test deleting a task via delete_task view."""
        task_id = self.task.id
        request = self.factory.get(reverse('delete_task', args=[task_id]))
        request.user = self.expertise_user
        response = delete_task(request, task_id)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task_id).exists())


class TaskComponentTests(TestCase):
    def setUp(self):
        """Sets up test data for Task component tests."""
        self.team_expertise = Group.objects.create(name="Team Expertise")
        self.expertise_user = User.objects.create_user(username="expert_user", password="testpass")
        self.expertise_user.groups.add(self.team_expertise)
        self.client.login(username="expert_user", password="testpass")

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
        response = self.client.get(reverse('archive'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("<strong>Land:</strong> Germany", content)
        self.assertNotIn("<strong>Land:</strong> Netherlands", content)

    def test_get_specific_task(self):
        """CT2: Verify a specific task is fetched via API."""
        response = self.client.get(reverse('view_task', args=[self.unarchived_task.id]))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(self.unarchived_task.country, content)
        self.assertNotIn(self.archived_task.country, content)

    def test_get_unarchived_tasks(self):
        """CT1: Verify all unarchived tasks are displayed in the rendered HTML."""
        response = self.client.get(reverse('kanban_board'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("<strong>Land:</strong> Netherlands", content)
        self.assertNotIn("<strong>Land:</strong> Germany", content)


class CommentIntegrationTest(LiveServerTestCase):
    def setUp(self):
        """Sets up the Selenium WebDriver and task data for Comment integration test."""
        # Set up ChromeOptions for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (not needed in headless)
        chrome_options.add_argument("--window-size=1920x1080")  # Set window size to avoid issues with elements being off-screen

        # Set up the WebDriver using webdriver_manager to handle chromedriver installation
        service = Service(ChromeDriverManager().install())  # Correctly set up the service with the chromedriver path
        self.browser = webdriver.Chrome(service=service, options=chrome_options)  # Use the options parameter here


        self.team_expertise = Group.objects.create(name="Team Expertise")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.user.groups.add(self.team_expertise)

        self.task = Task.objects.create(
            country="Netherlands",
            sector=SectorChoices.ZAAIZADEN,
            status=TaskStatus.TODO,
            column=ColumnStatus.EXPERTISE,
            assigned_employee=self.user,
            priority=PriorityChoices.HIGH,
            source="Source example",
            coverages="Coverage example",
            archived=False,
        )

    def tearDown(self):
        """Quits the browser after each test."""
        self.browser.quit()

    def login(self):
        """Helper method for logging in."""
        self.browser.get(f"{self.live_server_url}/")
        self.browser.find_element(By.NAME, "username").send_keys("testuser")
        self.browser.find_element(By.NAME, "password").send_keys("testpassword")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    def test_add_comment_to_task(self):
        """IT1: Test adding a comment to a task through the UI."""
        self.login()
        self.browser.get(f"{self.live_server_url}/")
        time.sleep(2)

        task_element = self.browser.find_element(By.CSS_SELECTOR, "a.task")
        task_element.click()

        time.sleep(1)
        comment_box = self.browser.find_element(By.NAME, "content")
        comment_box.send_keys("This is a test comment.")

        submit_button = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(1)
        self.assertIn("This is a test comment.", self.browser.page_source)

    def test_move_task_to_next_column(self):
        """IT2: Test moving a task to the next column through the UI."""
        self.login()
        self.browser.get(f"{self.live_server_url}/")
        time.sleep(2)

        task_element = self.browser.find_element(By.CSS_SELECTOR, "a.task")
        task_element.click()

        move_button = self.browser.find_element(By.NAME, "move-to-contentbeheer")
        move_button.click()

        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.NAME, "contentbeheer-column"))
        )

        contentbeheer_column = self.browser.find_element(By.NAME, "contentbeheer-column")
        tasks_in_contentbeheer = contentbeheer_column.find_elements(By.CSS_SELECTOR, "a.task")
        task_ids_in_contentbeheer = [task.get_attribute("id") for task in tasks_in_contentbeheer]

        self.assertIn(str(self.task.id), task_ids_in_contentbeheer)

        expertise_column = self.browser.find_element(By.NAME, "expertise-column")
        tasks_in_expertise = expertise_column.find_elements(By.CSS_SELECTOR, "a.task")
        task_ids_in_expertise = [task.get_attribute("id") for task in tasks_in_expertise]

        self.assertNotIn(str(self.task.id), task_ids_in_expertise)
