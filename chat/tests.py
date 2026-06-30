from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from chat_messages.models import Message

from .models import Conversation, ConversationMember


class ConversationModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )

    def test_str_private(self):
        conv = Conversation.objects.create(conversation_type="PRIVATE")
        conv.participants.add(self.user)
        self.assertEqual(str(conv), f"Conversation {conv.pk}")

    def test_str_group_with_name(self):
        conv = Conversation.objects.create(
            conversation_type="GROUP",
            name="My Group",
        )
        conv.participants.add(self.user)
        self.assertEqual(str(conv), "My Group")

    def test_str_group_without_name(self):
        conv = Conversation.objects.create(conversation_type="GROUP")
        conv.participants.add(self.user)
        self.assertEqual(str(conv), f"Group ({conv.pk})")

    def test_get_absolute_url(self):
        conv = Conversation.objects.create(conversation_type="PRIVATE")
        conv.participants.add(self.user)
        self.assertEqual(
            conv.get_absolute_url(),
            reverse("chat:conversation_detail", kwargs={"pk": conv.pk}),
        )


class ConversationMemberModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )
        self.conv = Conversation.objects.create(conversation_type="GROUP", name="Test")

    def test_str(self):
        member = ConversationMember.objects.create(
            conversation=self.conv, user=self.user
        )
        self.assertEqual(str(member), f"testuser in {self.conv}")

    def test_unique_together(self):
        ConversationMember.objects.create(
            conversation=self.conv, user=self.user
        )
        with self.assertRaises(Exception):
            ConversationMember.objects.create(
                conversation=self.conv, user=self.user
            )

    def test_defaults(self):
        member = ConversationMember.objects.create(
            conversation=self.conv, user=self.user
        )
        self.assertFalse(member.is_admin)
        self.assertFalse(member.is_muted)


class ConversationListViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )
        self.other = get_user_model().objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass1!",
        )

    def test_requires_login(self):
        response = self.client.get(reverse("chat:conversation_list"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('chat:conversation_list')}",
        )

    def test_shows_empty_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("chat:conversation_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No conversations yet.")

    def test_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("chat:conversation_list"))
        self.assertTemplateUsed(response, "chat/conversation_list.html")

    def test_shows_own_conversations_only(self):
        self.client.force_login(self.user)
        own = Conversation.objects.create()
        own.participants.add(self.user)
        other_conv = Conversation.objects.create()
        other_conv.participants.add(self.other)
        response = self.client.get(reverse("chat:conversation_list"))
        self.assertContains(response, f"/chat/{own.pk}/")
        self.assertNotContains(response, f"/chat/{other_conv.pk}/")


class ConversationDetailViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )
        self.other = get_user_model().objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass1!",
        )
        self.conv = Conversation.objects.create()
        self.conv.participants.add(self.user, self.other)

    def test_requires_login(self):
        response = self.client.get(
            reverse("chat:conversation_detail", kwargs={"pk": self.conv.pk})
        )
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('chat:conversation_detail', kwargs={'pk': self.conv.pk})}",
        )

    def test_shows_conversation(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("chat:conversation_detail", kwargs={"pk": self.conv.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["conversation"], self.conv)

    def test_requires_membership(self):
        stranger = get_user_model().objects.create_user(
            username="stranger",
            email="stranger@example.com",
            password="StrongPass1!",
        )
        self.client.force_login(stranger)
        response = self.client.get(
            reverse("chat:conversation_detail", kwargs={"pk": self.conv.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("chat:conversation_detail", kwargs={"pk": self.conv.pk})
        )
        self.assertTemplateUsed(response, "chat/conversation_detail.html")

    def test_context_contains_messages(self):
        self.client.force_login(self.user)
        msg = Message.objects.create(
            conversation=self.conv,
            sender=self.user,
            content="Hello!",
        )
        response = self.client.get(
            reverse("chat:conversation_detail", kwargs={"pk": self.conv.pk})
        )
        self.assertIn(msg, response.context["chat_messages"])


class ConversationCreateViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )
        self.other = get_user_model().objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass1!",
        )

    def test_requires_login(self):
        response = self.client.get(reverse("chat:conversation_create"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('chat:conversation_create')}",
        )

    def test_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("chat:conversation_create"))
        self.assertTemplateUsed(response, "chat/conversation_form.html")

    def test_create_private_conversation(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("chat:conversation_create"), {
            "conversation_type": "PRIVATE",
            "participants": [self.other.pk],
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Conversation.objects.count(), 1)
        conv = Conversation.objects.first()
        self.assertIn(self.user, conv.participants.all())
        self.assertIn(self.other, conv.participants.all())

    def test_create_group_conversation(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("chat:conversation_create"), {
            "conversation_type": "GROUP",
            "name": "My Group",
            "participants": [self.other.pk],
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Conversation.objects.count(), 1)
        conv = Conversation.objects.first()
        self.assertEqual(conv.name, "My Group")
        self.assertEqual(conv.conversation_type, "GROUP")

    def test_group_requires_name(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("chat:conversation_create"), {
            "conversation_type": "GROUP",
            "participants": [self.other.pk],
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "name",
            "Group name is required for group conversations.",
        )


class ConversationFormTest(TestCase):

    def setUp(self):
        self.other = get_user_model().objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass1!",
        )

    def test_valid_private(self):
        from .forms import ConversationForm
        form = ConversationForm(data={
            "conversation_type": "PRIVATE",
            "participants": [self.other.pk],
        })
        self.assertTrue(form.is_valid())

    def test_valid_group(self):
        from .forms import ConversationForm
        form = ConversationForm(data={
            "conversation_type": "GROUP",
            "name": "My Group",
            "participants": [self.other.pk],
        })
        self.assertTrue(form.is_valid())

    def test_group_missing_name(self):
        from .forms import ConversationForm
        form = ConversationForm(data={
            "conversation_type": "GROUP",
            "participants": [self.other.pk],
        })
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
