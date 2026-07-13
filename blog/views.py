from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from blog.forms import PostForm
from blog.models import Post


def home(request):
    posts_list = Post.objects.filter(status=Post.Status.PUBLISHED).order_by(
        "-published_at"
    )
    paginator = Paginator(posts_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/home.html",
        {
            "page_obj": page_obj,
        },
    )


def post_detail(request, slug):
    if request.user.is_authenticated:
        queryset = Post.objects.filter(
            Q(status=Post.Status.PUBLISHED) | Q(author=request.user)
        )
    else:
        queryset = Post.objects.filter(status=Post.Status.PUBLISHED)
    post = get_object_or_404(queryset, slug=slug)

    return render(request, "blog/post_detail.html", {"post": post})


@login_required
def user_posts(request):
    user_posts = Post.objects.filter(Q(author=request.user)).order_by("-published_at")

    paginator = Paginator(user_posts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/my_posts.html",
        {
            "page_obj": page_obj,
        },
    )


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Пост успешно создан.")
            return redirect("blog:post_detail", slug=post.slug)
    else:
        form = PostForm()
    return render(request, "blog/post_form.html", {"form": form, "action": "Создать"})


@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user:
        return HttpResponseForbidden("Вы не можете редактировать этот пост.")

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            messages.success(request, "Пост обновлён.")
            return redirect("blog:post_detail", slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(
        request, "blog/post_form.html", {"form": form, "action": "Редактировать"}
    )


@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user:
        return HttpResponseForbidden("Вы не можете удалить этот пост.")

    if request.method == "POST":
        post.delete()
        messages.success(request, "Пост удалён.")
        return redirect("blog:my_posts")

    return render(request, "blog/post_confirm_delete.html", {"post": post})
