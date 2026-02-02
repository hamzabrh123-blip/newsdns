from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'district', 'category', 'date', 'is_important')
    list_filter = ('district', 'category', 'date', 'is_important')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    list_editable = ('is_important',)
