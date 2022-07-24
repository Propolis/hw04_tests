from django.db import models
from django.contrib.auth import get_user_model

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        blank=True,
        null=True,
        max_length=200,
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
    )
    description = models.TextField(
        max_length=200,
    )

    def __str__(self):
        return self.title


class Post(CreatedModel):
    PRINT_TEXT_LENGHT = 15

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
        blank=True,
        null=True,
        max_length=2500,
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        help_text='Группа, к которой будет относиться пост',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name="posts",
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:self.PRINT_TEXT_LENGHT]

    class Meta:
        ordering = ["-pub_date"]


class Comment(CreatedModel):
    text = models.TextField(
        max_length=1500,
        blank=True,
        null=True,
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Комментарий",
        help_text='Комментарий, который будет относиться к посту',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name="comments",
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name="following",
    )
