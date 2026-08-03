# shopping/redirects.py
from django.urls import re_path
from django.views.generic import RedirectView
from .views import gone_view

# Sirf SEO/Redirects wale patterns
seo_urlpatterns = [
    
    # 1. Jo categories/products 100% active hain aur sirf unka path /shopping/ hua hai, unhe hi redirect karein.
    # Agar koi specific dead category hai, toh use yahan se hata kar neeche gone_view mein dalein.
    re_path(r'^product/(?P<path>.*)$', RedirectView.as_view(url='/shopping/product/%(path)s', permanent=True)),
    
    # 2. Baaki saare dead/news/location patterns jinko 410 (Gone) bhejna hai
    re_path(r'^(ai|basti|hollywood|gorakhpur-lucknow|sitapur|sambhal|prayagraj|ujjain|deoria|ghaziabad|technology|other-state|mahoba|agra|hyderabad|international|news|market|gonda|amethi|bahraich|bijnor|bollywood|Basti|Farrukhabad|kanpur-nagar|Kanpur-Dehat|gorakhpur|district|new-delhi|goa|mumbai|lucknow|national|google|delhi|saharanpur|shahjahanpur|shravasti|kannauj|market-news|sports|varanasi|toronto-canada|mathura|hapur|mainpuri|n)/.*$', gone_view), 
    
    # 3. Jo shopping categories dead hain, unhe seedha 410 bhejne ke liye yeh rule upar rakhen
    re_path(r'^shopping/category/(auraiya|ambedkar-nagar|Other-State|etah|Sonbhadra|kanpur|mainpuri|gorakhpur|UP-National|gautam-buddha-nagar|uttar-pradesh|kanpur-nagar|varanasi|sports|Sitapur|Shravasti|Moradabad|meerut|Rampur|chandauli|Farrukhabad|Prayagraj|Kanpur-Dehat|Shamli|etah|gonda|lucknow|Basti|pilibhit)/.*$', gone_view),

    # 4. GENERIC CATCH-ALL FOR OLD CATEGORIES: 
    # Agar aapki baaki saari purani categories bhi dead hain, toh unhe redirect karne ki bajaye seedha gone_view par bhejo, 
    # ya phir sirf unhi ko redirect karo jo database mein exist karti hain.
    re_path(r'^category/(?P<path>.*)$', gone_view),  # Agar saari purani categories khatam kar di hain toh redirect ki jagah gone_view lagayein!
]