from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import datetime
import uuid
from django.db.models import IntegerField, Model
from django.core.validators import MaxValueValidator, MinValueValidator


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None

    email = models.EmailField('email address', unique=True)
    bool_is_author = models.BooleanField(default=False, help_text='Designates whether user is an author', verbose_name='Author')
    bool_is_editor = models.BooleanField(default=False, help_text='Designates whether user is an editor', verbose_name='Editor')
    bool_is_executive_editor = models.BooleanField(default=False, help_text='Designates whether user is an executive editor', verbose_name='Executive editor')

    first_name = models.CharField('first name', max_length = 30, blank=False)
    last_name = models.CharField('last name', max_length = 30, blank=False)

    bio = models.TextField(blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    profile_pic = models.ImageField(default='default_profile_pic.jpg', blank=True, max_length=300)

    favorites = models.ManyToManyField('Article', related_name='favorites', blank=True)
    subscribe_author = models.ManyToManyField('User', blank=True)
    subscribe_tag = models.ManyToManyField('Tag', related_name='subscribe_tag', blank=True)
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    objects = UserManager()
    def get_image(self):
        if not self.profile_pic:
            return '/media/default_profile_pic.jpg'
        else:
            return self.profile_pic.url

    def is_author(self):
        return self.is_superuser or self.bool_is_author

    def is_editor(self):
        return self.bool_is_executive_editor or self.bool_is_editor or self.is_superuser

    def is_executive_editor(self):
        return self.is_superuser or self.bool_is_executive_editor

    def is_admin(self):
        return self.is_superuser

    def name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return self.first_name + " " + self.last_name


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=20)

    def __str__(self):
        return self.name


class Article(models.Model):
    author = models.ManyToManyField(User, related_name='author', limit_choices_to={'bool_is_author': True}, blank=True)
    title = models.CharField(max_length=100)
    text = models.TextField(default='Start typing here...')
    thumb = models.ImageField(default='default.png', blank=True, max_length=300)
    pub_date = models.DateTimeField(auto_now_add=True)
    tag = models.ManyToManyField(Tag, related_name='article_tag', blank=True)
    layout_choices = (('LO1', 'Normal'),
             ('LO2', 'Two columns'),
             ('LO3', 'Picture in middle'))
    layout = models.CharField(max_length=3, choices=layout_choices,default='LO1')
    is_published = models.BooleanField(default=False, help_text='Publish article')
    is_reviewed = models.BooleanField(default=False, help_text='Review article')
    assigned_proof_read = models.ManyToManyField(User, related_name="proof_read", limit_choices_to={'bool_is_editor': True}, blank = True)
    last_edited = models.DateTimeField(auto_now=True, blank=True)

    def get_image(self):
        if not self.thumb:
            return '/media/default.png'
        else:
            return self.thumb.url

    class Meta:
        ordering = ['-pub_date', ]

    def submit(self):
        self.save()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)


class RateComment(models.Model):
    post = models.ForeignKey(Article, related_name='ratecomments', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    rating = IntegerField("Rating 1-10",
        default=1,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ]
     )

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)


class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    role_choices = (
        ('', 'Request new role'),
        ('author', 'Author'),
        ('editor', 'Editor'),
        ('edit_and_author', 'Editor and author' ),
        ('exec', 'Executive editor'),
    )
    role = models.CharField(max_length=30, choices=role_choices, default='1')

    def __str__(self):
        return '{} {} requested {}'.format(self.user.first_name, self.user.last_name, self.role)


class ColorScheme(models.Model):
    color = models.CharField(max_length=100);

    @classmethod
    def create(cls, color):
        color = cls(color=color)
        return color

    def __str__(self):
        return self.color

class Layout(models.Model):
    one_column = 'layout_one_column.html'
    two_columns = 'layout_articles_side_by_side.html'
    big_two_columns = 'layout_big_article.html'
    layout_choices = ((one_column, 'One column'),( two_columns , 'Two columns'), (big_two_columns,'Big two columns'))
    layout = models.CharField(max_length=33, choices=layout_choices, default=one_column)

    def __str__(self):
        return self.layout
