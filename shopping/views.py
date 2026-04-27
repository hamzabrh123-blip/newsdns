from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from .models import HomeSlider # ऊपर इम्पोर्ट कर लेना

# इसे रख (इसमें स्लाइडर भी है)
def shop_home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    sliders = HomeSlider.objects.filter(is_active=True)
    return render(request, 'shopping/shop_home.html', {
        'categories': categories,
        'products': products,
        'sliders': sliders
    })

# 2. कैटेगरी वाला पेज (जब कोई 'Designer Kurti' पर क्लिक करे)
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    # सिर्फ उसी कैटेगरी के माल (Products) फिल्टर होकर आएंगे
    products = Product.objects.filter(category=category)
    categories = Category.objects.all() # ताकि ऊपर मेन्यू में बाकी कैटेगरी दिखती रहें
    return render(request, 'shopping/shop_home.html', {
        'category': category,
        'products': products,
        'categories': categories
    })

# 3. माल का पूरा ब्यौरा (Shanaya Style Detail Page)
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    # यहाँ भी कैटेगरी भेज रहे हैं ताकि नेवबार/मेन्यू में कैटेगरी दिखती रहें
    categories = Category.objects.all() 
    return render(request, 'shopping/product_detail.html', {
        'product': product,
        'categories': categories
    })
