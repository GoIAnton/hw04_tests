from posts.models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group',
            description='Тестовое описание',
        )
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
            'text': self.post.text,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': f'{self.post.author.username}'},
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=self.post.text,
            ).exists()
        )

    def test_post_edit(self):
        posts_count = Post.objects.count()
        form_data = {
            'author': self.user,
            'text': 'Измененный тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{self.post.id}'},
        ))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                id=1,
                author=self.user,
                text='Измененный тестовый текст',
                group=self.group,
            ).exists()
        )

    def test_create_and_edit_for_guest(self):
        self.guest_client = Client()
        response = self.guest_client.post(
            reverse('posts:post_create'),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('posts:post_create')
        )
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('users:login')
            + '?next='
            + reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'})
        )

    def test_edit_not_your_post(self):
        self.new_user = User.objects.create_user(username='NewName')
        self.new_post = Post.objects.create(
            author=self.new_user,
            text='Тестовый текст поста',
        )
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.new_post.id}'}
            ),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.new_post.id}))
