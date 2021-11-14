from .models import Category, Comment, Genre, Review, Title
from django.contrib import admin


class CategoryAdmin(admin.ModelAdmin):
    """Страница категорий в админке."""
    list_display = ('pk', 'name', 'slug')
    list_display_links = ('pk', 'name',)
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    prepopulated_fields = {'slug': ('name',)}


class GenreAdmin(admin.ModelAdmin):
    """Страница жанров в админке."""
    list_display = ('pk', 'name', 'slug',)
    list_display_links = ('pk', 'name',)
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    prepopulated_fields = {'slug': ('name',)}


class TitleAdmin(admin.ModelAdmin):
    """Страница произведений в админке."""
    list_display = ('pk', 'name', 'year', 'category')
    list_display_links = ('pk', 'name',)
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    """Страница комментариев в админке"""
    list_display = ('pk', 'reviews', 'author', 'text', 'pub_date')
    list_display_links = ('pk', 'text',)
    list_filter = ('author',)
    search_fields = ('author',)
    empty_value_display = '-пусто-'


class ReviewAdmin(admin.ModelAdmin):
    """Страница  в админке"""
    list_display = ('pk', 'title', 'score', 'author', 'text')
    list_display_links = ('pk', 'titles',)
    list_filter = ('author',)
    search_fields = ('author',)
    empty_value_display = '-пусто-'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Review, ReviewAdmin)
