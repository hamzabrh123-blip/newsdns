# shopping/redirects.py
from django.urls import re_path
from .views import gone_view

# Sirf SEO/Redirects wale patterns
seo_urlpatterns = [
    re_path(r'^(prayagraj|ujjain|deoria|ghaziabad|technology|other-state|shopping|mahoba|agra|hyderabad|international|news|market|gonda|amethi|bahraich|bijnor|bollywood|Basti|Farrukhabad|kanpur-nagar|Kanpur-Dehat|gorakhpur|district|new-delhi|goa|mumbai|lucknow|national|google|delhi|kannauj|market-news|sports|varanasi|toronto-canada|mathura|mainpuri|n)/.*$', gone_view), 
    re_path(r'^category/(uttar-pradesh|kanpur-nagar|varanasi|sports|Sitapur|Shravasti|Moradabad|meerut|Rampur|chandauli|Farrukhabad|Prayagraj|Kanpur-Dehat|ambedkar-nagar|gonda|lucknow|Basti|pilibhit)/.*$', gone_view),
]

