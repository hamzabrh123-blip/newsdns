from django.contrib.sitemaps import Sitemap
from .models import Product

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8  # न्यूज़ से थोड़ा ज़्यादा प्रायोरिटी

    def items(self):
        # -id का मतलब है लेटेस्ट प्रोडक्ट सबसे पहले सैटमैप में आएगा
        return Product.objects.all().order_by('-id')

    def lastmod(self, obj):
        # यहाँ 'created_at' इस्तेमाल कर रहे हैं
        return obj.created_at