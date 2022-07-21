from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("user", "пользователь"),
        ("moderator", "модератор"),
        ("admin", "администратор"),
    )

    role = models.CharField(
        max_length=25,
        verbose_name="Роль пользователя",
        choices=ROLE_CHOICES,
        default="user",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
    )
    bio = models.TextField(
        verbose_name="Биография",
        blank=True,
    )
    confirmation_code = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Код подтверждения",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Пользователь"


class Genre(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name="Название",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="URL",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Жанр"


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name="Название",
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="URL",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Категория"


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name="Название",
    )
    year = models.PositiveSmallIntegerField(
        db_index=True,
        verbose_name="Год",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name="Жанр",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="titles",
        blank=True,
        null=True,
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "Произведение"


class Review(models.Model):
    text = models.TextField(verbose_name="Текст отзыва")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор",
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message="Оценка не может быть меньше 1"),
            MaxValueValidator(10, message="Оценка не может быть выше 10"),
        ],
        verbose_name="Оценка",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        blank=False,
        null=False,
        verbose_name="Произведение",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_review"
            )
        ]
        verbose_name = "Отзыв"


class Comment(models.Model):
    text = models.TextField(
        blank=False,
        verbose_name="Текст комментария",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        blank=False,
        null=False,
        verbose_name="Отзыв",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )

    class Meta:
        verbose_name = "Комментарий"
