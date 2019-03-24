from django.test import TestCase
from .models import *
from django.utils import timezone
from django.test import Client

# Create your tests here.
class UserTestCase(TestCase):

    def setUp(self):
      #  time = timezone.now()

        self.author = User.objects.create(first_name="Per", last_name="Fuglesang", email="test1@test1.test1", bool_is_author=True)
        User.objects.create(first_name="Kari", last_name="Fugl", email="test2@test2.test2", bool_is_editor=True)
        User.objects.create(first_name="Ola", last_name="Tann", email="test3@test3.test3", bool_is_executive_editor=True)

        Tag.objects.create(name="Sport")

        Article.objects.create(title="it prosjekt", text="It prosjekt suger", pub_date=timezone.now())

        self.c = Client()
       # UserManager.create_user(self, email="test@test.test", password="test123")
        User.objects.create(email="test@test.test", password=("test123"))
    def test_author_fields(self):
        """all fields are correct"""
        user_object = User.objects.get(first_name="Per")
        self.assertEqual(user_object.is_author(), True)
        self.assertEqual(user_object.email, "test1@test1.test1")
        self.assertEqual(user_object.last_name, "Fuglesang")

    def test_editor_fields(self):
        """all fields are correct"""
        user_object = User.objects.get(first_name="Kari")
        self.assertEqual(user_object.is_editor(), True)
        self.assertEqual(user_object.email, "test2@test2.test2")
        self.assertEqual(user_object.last_name, "Fugl")

    def test_exec_editor_fields(self):
        """all fields are correct"""
        user_object = User.objects.get(first_name="Ola")
        self.assertEqual(user_object.is_executive_editor(), True)
        self.assertEqual(user_object.email, "test3@test3.test3")
        self.assertEqual(user_object.last_name, "Tann")

    def test_tag_fields(self):
        tag_object = Tag.objects.get(name="Sport")
        self.assertEqual(tag_object.name, "Sport")

    def test_article_fields(self):
        article_object = Article.objects.get(title="it prosjekt")
        self.assertEqual(article_object.title, "it prosjekt")


    def test_registered_user_read_article(self):
        self.c.login(username="test@test.test", password="test123")
        response = self.c.get('/post/1/')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.content, '{}')


