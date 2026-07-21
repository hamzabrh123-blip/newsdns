# shopping/redirects.py
from django.urls import re_path
from django.views.generic import RedirectView
from .views import gone_view

# Sirf SEO/Redirects wale patterns
seo_urlpatterns = [
   
   # Purane bina /shopping/ wale links ko /shopping/ par redirect karne ke liye
    re_path(r'^category/(?P<path>.*)$', RedirectView.as_view(url='/shopping/category/%(path)s', permanent=True)),
    re_path(r'^product/(?P<path>.*)$', RedirectView.as_view(url='/shopping/product/%(path)s', permanent=True)),
    
    # Baaki dead/news/location patterns jinko 410 (Gone) bhejna hai
    re_path(r'^(hollywood|gorakhpur-lucknow|sitapur|sambhal|prayagraj|ujjain|deoria|ghaziabad|technology|other-state|mahoba|agra|hyderabad|international|news|market|gonda|amethi|bahraich|bijnor|bollywood|Basti|Farrukhabad|kanpur-nagar|Kanpur-Dehat|gorakhpur|district|new-delhi|goa|mumbai|lucknow|national|google|delhi|kannauj|market-news|sports|varanasi|toronto-canada|mathura|mainpuri|n)/.*$', gone_view), 
    re_path(r'^category/(Other-State|etah|Sonbhadra|kanpur|mainpuri|gorakhpur|UP-National|gautam-buddha-nagar|uttar-pradesh|kanpur-nagar|varanasi|sports|Sitapur|Shravasti|Moradabad|meerut|Rampur|chandauli|Farrukhabad|Prayagraj|Kanpur-Dehat|ambedkar-nagar|gonda|lucknow|Basti|pilibhit)/.*$', gone_view),
]