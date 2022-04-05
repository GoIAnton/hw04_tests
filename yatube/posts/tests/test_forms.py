from posts.forms import PostForm
from posts.models import Post
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.form = PostForm()
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        posts_count = Post.objects.count()
        form_data = {
            'author': self.user,
            'text': 'Тестовый текст поста',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'Name'},
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Тестовый текст поста'
            ).exists()
        )

    def test_post_edit(self):
        form_data = {
            'author': self.user,
            'text': 'Измененный тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': '1'},
        ))
        self.assertTrue(
            Post.objects.filter(
                id=1,
                author=self.user,
                text='Измененный тестовый текст'
            ).exists()
        )
