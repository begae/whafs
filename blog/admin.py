from django.contrib import admin
from .models import Comment, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'published', 'status']
    list_filter = ['status', 'created', 'published', 'author']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published'
    ordering = ['status', 'published']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['by_name', 'by_email', 'on_post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['by_name', 'by_email', 'body']