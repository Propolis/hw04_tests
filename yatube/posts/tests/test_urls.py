import unittest

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Название группы",
            slug="test-slug",
            description="описание",
        )
        cls.user_author = User.objects.create_user(
            username="HasNoName",
        )
        cls.post = Post.objects.create(
            text="Текст",
            author_id=cls.user_author.id
        )
        cls.user_not_author = User.objects.create_user(
            username="NotAuthorPost"
        )
        cls.authorized_client_not_author = Client()
        cls.authorized_client_not_author.force_login(cls.user_not_author)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = StaticURLTests.user_author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @unittest.skip
    def test_the_page_is_available_to_any_user(self):
        """Страница доступна любому пользователю"""
        pages = {
            "/": 200,
            "/group/test-slug/": 200,
            "/profile/HasNoName/": 200,
            f"/posts/{self.post.pk}/": 200,
            "/unexisting_page/": 404,
        }
        for url, status_code in pages.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    @unittest.skip
    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного
                пользователя на страницу логина."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    @unittest.skip
    def test_post_edit_is_available_only_to_the_author(self):
        """Страница /posts/<post_id>/edit/ доступна только автору"""
        response = self.authorized_client.get(f"/posts/{self.post.pk}/edit/")
        self.assertEqual(response.status_code, 200)

    @unittest.skip
    def test_post_edit_url_redirect_not_author_on_post_detail(self):
        """Страница /posts/<post_id>/edit/ перенаправит не автора на страницу
        /posts/<post_id>/"""
        response = self.authorized_client_not_author.get(
            f"/posts/{self.post.pk}/edit/")
        self.assertRedirects(
            response, f'/posts/{self.post.pk}/'
        )

    @unittest.skip
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "/": "posts/index.html",
            f"/group/{self.group.slug}/": "posts/group_list.html",
            f"/profile/{self.user_author.username}/": "posts/profile.html",
            f"/posts/{self.post.pk}/": "posts/post_detail.html",
            f"/posts/{self.post.pk}/edit/": "posts/create_post.html",
            "/create/": "posts/create_post.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
