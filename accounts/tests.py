from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Workspace

User = get_user_model()


class WorkspaceSignalTests(TestCase):
    def test_creating_user_creates_workspace(self):
        user = User.objects.create_user(username="martin", password="pass12345")
        self.assertTrue(Workspace.objects.filter(owner=user).exists())