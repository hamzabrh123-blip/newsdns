from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    # 1. Ye saare columns aapko admin panel mein saamne dikhenge
    # 'url_city' ko 'district' ke baad rakha hai taaki asani ho
    list_display = ('title', 'district', 'category', 'date', 'is_important')
    
    # 2. Side mein filter (District ab Dropdown hai toh filter mast kaam karega)
    list_filter = ('district', 'category', 'date')
    
    # 3. Search bar: Title aur Content se news dhoondne ke liye
    search_fields = ('title', 'content')
    
    # 4. News likhte waqt Slug apne aap ban jaye (Auto-fill)
    prepopulated_fields = {'slug': ('title',)}
    
    # 5. Ek page par kitni news dikhe
    list_per_page = 20

# 'admin.site.register(District)' ko maine hata diya hai 
# kyunki ab District model exist nahi karta.
