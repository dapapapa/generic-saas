from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Workspace
from flow.rules import WIP_LIMITS
from flow.models import WorkItem

User = get_user_model()


class FlowBoardTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="pass12345")
        self.u2 = User.objects.create_user(username="u2", password="pass12345")

        # IMPORTANT: match _get_workspace() behavior (owner-based)
        self.ws1 = Workspace.objects.get(owner=self.u1)
        self.ws2 = Workspace.objects.get(owner=self.u2)

        WorkItem.objects.create(
            workspace=self.ws1, title="U1 Item", status="released", created_by=self.u1
        )
        WorkItem.objects.create(
            workspace=self.ws2, title="U2 Item", status="released", created_by=self.u2
        )

    def test_board_shows_only_users_work_items(self):
        ok = self.client.login(username="u1", password="pass12345")
        self.assertTrue(ok)

        resp = self.client.get(reverse("flow-board"))
        self.assertEqual(resp.status_code, 200)

        self.assertContains(resp, "U1 Item")
        self.assertNotContains(resp, "U2 Item")


class FlowTransitionTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="pass12345")
        self.ws1 = Workspace.objects.get(owner=self.u1)
        self.i1 = WorkItem.objects.create(
            workspace=self.ws1,
            title="Movable item",
            status="ready",
            created_by=self.u1,
        )

    def test_wip_limit_blocks_move(self):
        dest = "packed"
        limit = WIP_LIMITS.get(dest)

        if limit is None:
            self.skipTest("No WIP limit configured for test destination")

        ok = self.client.login(username="u1", password="pass12345")
        self.assertTrue(ok)

        for i in range(limit):
            WorkItem.objects.create(
                workspace=self.ws1,
                title=f"Filler {i}",
                status=dest,
                created_by=self.u1,
            )

        original_status = self.i1.status

        resp = self.client.post(
            reverse("flow-move-workitem", args=[self.i1.id, dest]),
            follow=True,
        )

        self.assertEqual(resp.status_code, 200)
        self.i1.refresh_from_db()
        self.assertEqual(self.i1.status, original_status)
