from django.urls import path

from blog import views

app_name = "blog"

urlpatterns = [
    path("", views.home, name="home"),
    path("post/new/", views.post_create, name="post_create"),
    path("post/<slug:slug>/edit/", views.post_edit, name="post_edit"),
    path("post/<slug:slug>/delete/", views.post_delete, name="post_delete"),
    path("my-posts/", views.user_posts, name="my_posts"),
    path("post/<slug:slug>/", views.post_detail, name="post_detail"),
]
