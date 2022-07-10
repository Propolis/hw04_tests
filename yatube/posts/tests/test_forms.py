from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Post, Group


User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="user")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            text="Текст",
            author_id=cls.user.id
        )
        cls.group = Group.objects.create(
            title="Название группы",
            description="Описание",
            slug="test-slug",
        )
        cls.group_2 = Group.objects.create(
            title="Название группы",
            description="Описание",
            slug="test-slug_2",
        )

    def test_create_post(self):
        count_posts_before = Post.objects.count()
        data = {
            "text": "Текст",
            "group": self.group.id
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=data,
            follow=True,
        )
        count_posts_after = Post.objects.count()
        self.assertEqual(count_posts_after, count_posts_before + 1)
        self.assertTrue(
            Post.objects.filter(
                text="Текст",
                group_id=self.group.id,
            ).exists()
        )
        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={"username": self.user.username})
        )

    def test_edit_post(self):
        data = {
            "text": "Новый текст",
            "group": self.group_2.id
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            data=data,
            follow=True,
        )
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.text, data["text"])
        self.assertEqual(post.group.id, data["group"])
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
