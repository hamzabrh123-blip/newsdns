from django.urls import path
from django.http import HttpResponse
from . import views

# --- SEO & Utility Functions ---

def robots_txt(request):
    content = "User-agent: *\nDisallow: /admin/\nAllow: /\n\nSitemap: https://uttarworld.com/sitemap.xml"
    return HttpResponse(content, content_type="text/plain")

def ads_txt(request):
    content = "google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")

# --- URL Patterns ---

urlpatterns = [
    # 1. होम पेज
    path('', views.shop_home, name='shop_home'),
    
    # 2. सर्च और फिल्टर
    path('search/', views.product_search, name='product_search'), 
    
    # 3. कैटेगरी और प्रोडक्ट
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # 4. ELITE POLICY & ABOUT PAGES
    path('about_us/', views.about_us, name='about_us'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('terms/', views.terms_of_service, name='terms'),
    path('contact/', views.contact_us, name='contact'),
    
    # 5. SEO & AdSense Files
    path('sitemap.xml', views.sitemap_shop_xml, name='sitemap_shop_xml'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('ads.txt', ads_txt, name='ads_txt'),
]