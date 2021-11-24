from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

from .validators import score_validation, text_validation


class User(AbstractUser):
    email = models.EmailField(
        'email', max_length=254, blank=False, unique=True
    )
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, USER),
        (MODERATOR, MODERATOR),
        (ADMIN, ADMIN),
    ]
    role = models.CharField(
        'role',
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
    )
    bio = models.TextField('biography', blank=True)
    confirmation_code = models.CharField(max_length=254)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', ],
                name='unique_username'
            ),
            models.UniqueConstraint(
                fields=['email', ],
                name='unique_email'
            ),
            models.CheckConstraint(
                check=~Q(username__iexact='me'),
                name='cant_given_username'
            ),
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR


class Category(models.Model):
    name = models.CharField(
        max_length=256, db_index=True,
        verbose_name='Название категории',
        help_text='Укажите название для категории'
    )
    slug = models.SlugField(
        max_length=256, unique=True,
        verbose_name='Slug для категории',
        help_text='Задайте уникальный Slug категории.'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=256, db_index=True,
        verbose_name='Название жанра',
        help_text='Укажите название жанра'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug жанра',
        help_text='Задайте уникальный Slug жанра'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256, db_index=True,
        verbose_name='Название произведения',
        help_text='Укажите название произведения'
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год выпуска',
        help_text='Задайте год выпуска'
    )
    description = models.TextField(
        null=True, blank=True, verbose_name='Описание'
    )
    category = models.ForeignKey(
        Category, verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name='titles', blank=True, null=True
    )
    genre = models.ManyToManyField(
        Genre, verbose_name='Жанр',
        related_name='titles', blank=True
    )
    rating = models.IntegerField(
        verbose_name='Оценка',
        validators=[score_validation],
        null=True,
        default=None
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField(
        'text',
        validators=[text_validation],
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_author',
        verbose_name='пользователь'
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведения',
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[score_validation],
        default=0,
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title',),
                name='unique_subscribers'),
        )
        ordering = ('id',)


class Comment(models.Model):
    text = models.TextField('text')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments',
    )
    reviews = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='произведения',
        related_name='comments',
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('id',)
