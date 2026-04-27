from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop_home, name='shop_home'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'), # यह पक्का जोड़ लेना
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]