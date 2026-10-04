from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Category, Task

User = get_user_model()


class TaskMvpTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username="alice", password="StrongPass123")
        self.user_b = User.objects.create_user(username="bob", password="StrongPass123")
        self.category_a = Category.objects.create(user=self.user_a, name="Учёба")
        self.task_a = Task.objects.create(
            user=self.user_a,
            title="Почитать Django",
            category=self.category_a,
            description="Три раздела по проекту.",
        )

    def test_unauthenticated_tasks_redirect_to_login(self):
        response = self.client.get(reverse("task_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_registration_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("register"),
            {"username": "carol", "password1": "StrongPass123", "password2": "StrongPass123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task_list"))
        self.assertTrue(User.objects.filter(username="carol").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_task_creation_binds_to_request_user(self):
        self.client.force_login(self.user_a)
        response = self.client.post(
            reverse("task_create"),
            {
                "title": "Новая задача",
                "description": "Описание задачи",
                "category": self.category_a.pk,
                "due_date": "",
                "completed": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(user=self.user_a, title="Новая задача").exists())

    def test_user_b_cannot_access_user_a_task(self):
        self.client.force_login(self.user_b)
        endpoints = [
            reverse("task_detail", args=[self.task_a.pk]),
            reverse("task_update", args=[self.task_a.pk]),
            reverse("task_delete", args=[self.task_a.pk]),
        ]
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 404)

        response = self.client.post(reverse("task_toggle", args=[self.task_a.pk]))
        self.assertEqual(response.status_code, 404)

    def test_user_b_task_list_does_not_include_user_a_task(self):
        self.client.force_login(self.user_b)
        response = self.client.get(reverse("task_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.task_a.title)

    def test_delete_via_get_does_not_delete_but_post_does(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse("task_delete", args=[self.task_a.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Task.objects.filter(pk=self.task_a.pk).exists())

        response = self.client.post(reverse("task_delete", args=[self.task_a.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=self.task_a.pk).exists())
