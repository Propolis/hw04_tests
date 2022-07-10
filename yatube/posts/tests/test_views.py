from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group
from django import forms

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.user = User.objects.create_user(username="user_1")
        cls.post = Post.objects.create(
            text="Текст1",
            author_id=cls.user.id,
            group_id=cls.group.id,
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user_2 = User.objects.create_user(username="user_2")
        Post.objects.create(
            text="Текст2",
            author_id=cls.user_2.id,
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse("posts:post_create"): "posts/create_post.html",
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}): "posts/group_list.html",
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}): "posts/profile.html",
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.post.id}): "posts/post_detail.html",
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.post.id}): "posts/create_post.html",
        }
        for url, template in templates_pages_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        second_object = response.context["page_obj"][1]
        self.assertEqual(first_object.text, "Текст2")
        self.assertEqual(second_object.text, "Текст1")

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug}))
        objects = response.context["page_obj"]
        for obj in objects:
            with self.subTest(object=obj):
                self.assertEqual(obj.group.slug, self.group.slug)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": self.user.username}))
        objects = response.context["page_obj"]
        for obj in objects:
            with self.subTest(object=obj):
                self.assertEqual(obj.author.username, self.user.username)
        self.assertEqual(objects[0].text, "Текст1")

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk}))
        objects = response.context["post"]
        self.assertIsInstance(objects, Post)
        self.assertEqual(objects.text, "Текст1")

    def test_create_and_edit_post_page_show_correct_context(self):
        responses = (self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk})),
                     self.authorized_client.get(reverse("posts:post_create"))
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                for response in responses:
                    form_field = response.context.get("form").fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_create_post(self):
        pages = (reverse("posts:index"),
                 reverse("posts:group_list", kwargs={"slug": self.group.slug}),
                 reverse(
                     "posts:profile", kwargs={"username": self.user.username}),
                 )
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                objects = response.context.get("page_obj")
                self.assertIn(self.post, objects)
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group_2.slug}))
        objects = response.context.get("page_obj")
        self.assertNotIn(self.post, objects)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Название группы",
            description="Описание",
            slug="test-slug"
        )
        cls.user = User.objects.create_user(username="Aboba")
        cls.client = Client()
        cls.client.force_login(cls.user)
        for i in range(1, 14):
            Post.objects.create(
                text="Текст1",
                author_id=cls.user.id,
                group_id=cls.group.id,
            )

    def test_paginator_for_all_pages(self):
        pages = (
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.user.username}),
        )
        count = 0
        for i in ([i for i in range(0, 3)] * 2):
            if count > 2:
                response = self.client.get(pages[i] + "?page=2")
                self.assertEqual(len(response.context["page_obj"]), 3)
            else:
                response = self.client.get(pages[i])
                self.assertEqual(len(response.context["page_obj"]), 10)
            count += 1
