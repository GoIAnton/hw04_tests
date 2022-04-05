from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User
from .forms import PostForm


def create_page_obj(request, post_list):
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    post_list = (
        Post.objects.select_related('group').
        order_by('-pub_date')
    )
    page_obj = create_page_obj(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = (
        group.posts.select_related('group').
        order_by('-pub_date')
    )
    page_obj = create_page_obj(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = User.objects.get(username=username)
    post_list = (
        author.posts.select_related('group').
        order_by('-pub_date')
    )
    page_obj = create_page_obj(request, post_list)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            username = request.user
            instance.author = username
            instance.save()
            return redirect('posts:profile', username)
        return render(
            request,
            'posts/create_post.html',
            {'form': form, 'is_edit': False}
        )
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': False}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect(f'/posts/{post_id}/')
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
        return render(
            request,
            'posts/create_post.html',
            {'form': form, 'is_edit': True, 'post': post}
        )
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': True, 'post': post}
    )
