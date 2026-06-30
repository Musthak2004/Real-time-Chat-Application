from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from chat.models import Conversation

from .forms import MessageForm
from .models import Message, MessageReaction, MessageRead


class MessageModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )
        self.conv = Conversation.objects.create()
        self.conv.participants.add(self.user)

    def test_str_with_content(self):
        msg = Message.objects.create(
            conversation=self.conv,
            sender=self.user,
            content="Hello world!",
        )
        self.assertEqual(str(msg), "testuser: Hello world!")

    def test_str_with_attachment(self):
        msg = Message.objects.create(
            conversation=self.conv,
            sender=self.user,
            content="",
            message_type="IMAGE",
        )
        self.assertEqual(str(msg), "testuser: [attachment]")

    def test_truncates_long_content(self):
        msg = Message.objects.create(
            conversation=self.conv,
            sender=self.user,
            content="x" * 100,
        )
        result = str(msg)
        self.assertIn("testuser:", result)
        self.assertTrue(len(result) < 80)

    def test_default_message_type(self):
        msg = Message.objects.create(
            conversation=self.conv,
            sender=self.user,
            content="Hi",
        )
        self.assertEqual(msg.message_type, "TEXT")

    def test_default_is_edited(self):
        msg = Message.objects.create(
            conversation=self.conv,
            sender=self.user,
            content="Hi",
        )
        self.assertFalse(msg.is_edited)

    def test_ordering(self):
        msg1 = Message.objects.create(
            conversation=self.conv, sender=self.user, content="First",
        )
        msg2 = Message.objects.create(
            conversation=self.conv, sender=self.user, content="Second",
        )
        messages = Message.objects.all()
        self.assertEqual(list(messages), [msg1, msg2])


class MessageReadModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )
        self.conv = Conversation.objects.create()
        self.conv.participants.add(self.user)
        self.msg = Message.objects.create(
            conversation=self.conv,
            sender=self.user,
            content="Hello!",
        )

    def test_str(self):
        read = MessageRead.objects.create(message=self.msg, user=self.user)
        self.assertEqual(str(read), f"testuser read #{self.msg.pk}")

    def test_unique_together(self):
        MessageRead.objects.create(message=self.msg, user=self.user)
        with self.assertRaises(Exception):
            MessageRead.objects.create(message=self.msg, user=self.user)


class MessageReactionModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )
        self.conv = Conversation.objects.create()
        self.conv.participants.add(self.user)
        self.msg = Message.objects.create(
            conversation=self.conv,
            sender=self.user,
            content="Hello!",
        )

    def test_str(self):
        reaction = MessageReaction.objects.create(
            message=self.msg, user=self.user, emoji="👍"
        )
        self.assertEqual(str(reaction), "testuser reacted 👍")

    def test_unique_together(self):
        MessageReaction.objects.create(
            message=self.msg, user=self.user, emoji="👍",
        )
        with self.assertRaises(Exception):
            MessageReaction.objects.create(
                message=self.msg, user=self.user, emoji="❤️",
            )


class MessageFormTest(TestCase):

    def test_valid_text_message(self):
        form = MessageForm(data={
            "message_type": "TEXT",
            "content": "Hello!",
        })
        self.assertTrue(form.is_valid())

    def test_text_message_requires_content(self):
        form = MessageForm(data={
            "message_type": "TEXT",
            "content": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_image_message_requires_attachment(self):
        form = MessageForm(data={
            "message_type": "IMAGE",
            "content": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("attachment", form.errors)

    def test_file_message_requires_attachment(self):
        form = MessageForm(data={
            "message_type": "FILE",
            "content": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("attachment", form.errors)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class MessageCreateViewTest(TestCase):

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
            reverse("chat_messages:send_message", kwargs={"conversation_id": self.conv.pk})
        )
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('chat_messages:send_message', kwargs={'conversation_id': self.conv.pk})}",
        )

    def test_requires_membership_get(self):
        stranger = get_user_model().objects.create_user(
            username="stranger",
            email="stranger@example.com",
            password="StrongPass1!",
        )
        self.client.force_login(stranger)
        response = self.client.get(
            reverse("chat_messages:send_message", kwargs={"conversation_id": self.conv.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_requires_membership_post(self):
        stranger = get_user_model().objects.create_user(
            username="stranger",
            email="stranger@example.com",
            password="StrongPass1!",
        )
        self.client.force_login(stranger)
        response = self.client.post(
            reverse("chat_messages:send_message", kwargs={"conversation_id": self.conv.pk}),
            {"content": "Hello!", "message_type": "TEXT"},
        )
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("chat_messages:send_message", kwargs={"conversation_id": self.conv.pk})
        )
        self.assertTemplateUsed(response, "chat_messages/message_form.html")

    def test_create_message(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("chat_messages:send_message", kwargs={"conversation_id": self.conv.pk}),
            {"content": "Hello!", "message_type": "TEXT"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.count(), 1)
        msg = Message.objects.first()
        self.assertEqual(msg.content, "Hello!")
        self.assertEqual(msg.sender, self.user)
        self.assertEqual(msg.conversation, self.conv)

    def test_redirects_to_conversation_detail(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("chat_messages:send_message", kwargs={"conversation_id": self.conv.pk}),
            {"content": "Hi", "message_type": "TEXT"},
        )
        self.assertRedirects(
            response,
            reverse("chat:conversation_detail", kwargs={"pk": self.conv.pk}),
        )

    def test_context_contains_conversation(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("chat_messages:send_message", kwargs={"conversation_id": self.conv.pk})
        )
        self.assertEqual(response.context["conversation"], self.conv)

    def test_context_contains_messages(self):
        self.client.force_login(self.user)
        existing = Message.objects.create(
            conversation=self.conv, sender=self.user, content="Earlier",
        )
        response = self.client.get(
            reverse("chat_messages:send_message", kwargs={"conversation_id": self.conv.pk})
        )
        self.assertIn(existing, response.context["chat_messages"])
