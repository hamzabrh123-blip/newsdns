from django.contrib import admin
from .models import News, District

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    # 1. Ye saare columns aapko admin panel mein saamne dikhenge
    list_display = ('title', 'url_city', 'category', 'district', 'date', 'is_important')
    
    # 2. Side mein filter lag jayega jisse aap city/district wise news dekh sakte ho
    list_filter = ('district', 'category', 'date', 'url_city')
    
    # 3. Search bar: Title se news dhoondne ke liye
    search_fields = ('title', 'content')
    
    # 4. Ek page par kitni news dikhe
    list_per_page = 20

# District ko register rehne do
admin.site.register(District)
