from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "status", "author", "created_at")
    search_fields = ("title", "slug", "author__email", "content")
    list_filter = ("status", "created_at", "published_at")
    ordering = ("-created_at",)
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("author",)
