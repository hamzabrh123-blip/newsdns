from django.contrib import admin

from .models import News

class MynewsAdmin(admin.ModelAdmin):
    list_display = ('headline', 'date', 'is_important')
    list_filter = ('is_important', 'date')
    search_fields = ('headline',)

admin.site.register(News, MynewsAdmin)
