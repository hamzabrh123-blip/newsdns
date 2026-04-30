from django.shortcuts import render, get_object_or_404
from .models import Product, Category, HomeSlider

# 1. होम पेज (स्लाइडर और लेटेस्ट प्रोडक्ट्स)
def shop_home(request):
    categories = Category.objects.all()
    # .order_by('-id') जोड़ा ताकि नई पोस्ट सबसे ऊपर आए
    products = Product.objects.all().order_by('-id')
    sliders = HomeSlider.objects.filter(is_active=True).order_by('-id')
    
    return render(request, 'shopping/shop_home.html', {
        'categories': categories,
        'products': products,
        'sliders': sliders
    })

# 2. कैटेगरी वाला पेज (फिल्टर के साथ लेटेस्ट ऊपर)
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    # सिर्फ उसी कैटेगरी के माल और वो भी लेटेस्ट सबसे पहले
    products = Product.objects.filter(category=category).order_by('-id')
    categories = Category.objects.all() 
    
    return render(request, 'shopping/shop_home.html', {
        'category': category,
        'products': products,
        'categories': categories
    })

# 3. प्रोडक्ट डिटेल पेज
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    categories = Category.objects.all() 
    
    return render(request, 'shopping/product_detail.html', {
        'product': product,
        'categories': categories
    })