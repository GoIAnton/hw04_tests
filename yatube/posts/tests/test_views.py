from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.group1 = Group.objects.create(
            title='Группа1',
            slug='group1',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Группа2',
            slug='group2',
            description='Тестовое описание',
        )
        for i in range(12):
            exec(
                "post{} = Post.objects.create("
                "author=cls.user,"
                "text='Тестовый текст поста',"
                "group=cls.group1)".format(i)
            )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
        )
        cls.post_with_group = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
            group=cls.group1
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'group1'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'Name'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
            'posts/post_detail.html',
            reverse('posts:post_create'):
            'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
            'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_with_paginator_show_correct_context(self):
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'group1'}),
            reverse('posts:profile', kwargs={'username': 'Name'}),
        ]
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse('posts:index'))
                first_object = response.context['page_obj'][0]
                task_author_0 = first_object.author
                task_text_0 = first_object.text
                self.assertEqual(task_author_0, self.user)
                self.assertEqual(task_text_0, 'Тестовый текст поста')

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': '1'}
        ))
        first_object = response.context['post']
        task_author = first_object.author
        task_text = first_object.text
        self.assertEqual(task_author, self.user)
        self.assertEqual(task_text, 'Тестовый текст поста')

    def test_pages_with_form_show_correct_context(self):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        pages_names = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
        ]

        for reverse_name in pages_names:
            response = self.authorized_client.get(reverse_name)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_paginator(self):
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'group1'}),
            reverse('posts:profile', kwargs={'username': 'Name'}),
        ]
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_post_with_group1(self):
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'group1'}),
            reverse('posts:profile', kwargs={'username': 'Name'}),
        ]
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn(
                    self.post_with_group,
                    response.context['page_obj']
                )

    def test_post_with_group1_in_group2(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'group2'}
        ))
        self.assertNotIn(
            self.post_with_group,
            response.context['page_obj']
        )
