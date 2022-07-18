from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

import shutil
import tempfile

from ..models import Post, Group


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username="user")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            text="Текст",
            author_id=cls.user.id,
            image=cls.uploaded,
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_create_post_authorized_client(self):
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
        post = Post.objects.latest("pub_date")
        self.assertEqual(post.text, data["text"])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author_id, self.user.id)
        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={"username": self.user.username})
        )

    def test_create_post_guest_client(self):
        count_posts_before = Post.objects.count()
        data = {
            "text": "Текст",
            "group": self.group.id
        }
        response = self.guest_client.post(
            reverse("posts:post_create"),
            data=data,
            follow=True,
        )
        count_posts_after = Post.objects.count()
        self.assertEqual(count_posts_before, count_posts_after)
        self.assertRedirects(
            response,
            "/auth/login/?next=/create/",
        )

    def test_create_post_with_image(self):
        count_posts_before = Post.objects.all().count()
        data = {
            "text": "Текст",
            "image": self.uploaded.name
        }
        self.authorized_client.post(
            reverse("posts:post_create"),
            data=data,
            follow=True,
        )
        count_posts_after = Post.objects.all().count()
        self.assertEqual(count_posts_after, count_posts_before + 1)

    def test_edit_post(self):
        data = {
            "text": "Новый текст",
            "group": self.group_2.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            data=data,
            follow=True,
        )
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.text, data["text"])
        self.assertEqual(post.group, self.group_2)
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
