from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Workspace
from core.models import Project

User = get_user_model()


class WorkspaceIsolationTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="pass12345")
        self.u2 = User.objects.create_user(username="u2", password="pass12345")

        self.ws1 = Workspace.objects.get(owner=self.u1)
        self.ws2 = Workspace.objects.get(owner=self.u2)

        self.p1 = Project.objects.create(workspace=self.ws1, name="U1 Project")

    def test_user_sees_only_their_projects_on_list(self):
        self.client.login(username="u2", password="pass12345")
        resp = self.client.get(reverse("project_list"))
        self.assertContains(resp, "Projects")
        self.assertNotContains(resp, "U1 Project")

    def test_user_cannot_edit_other_users_project(self):
        self.client.login(username="u2", password="pass12345")
        resp = self.client.get(reverse("project_update", args=[self.p1.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_user_cannot_delete_other_users_project(self):
        self.client.login(username="u2", password="pass12345")
        resp = self.client.get(reverse("project_delete", args=[self.p1.pk]))
        self.assertEqual(resp.status_code, 404)