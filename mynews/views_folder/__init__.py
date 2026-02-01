# views_folder/__init__.py

# 1. News aur Categories (news_views.py se)
from .news_views import (
    home, 
    news_detail, 
    market_news_view, 
    national_news, 
    international_news, 
    technology, 
    bollywood, 
    district_news
)

# 2. Information Pages (info_views.py se)
from .info_views import (
    contact_us, 
    privacy_policy, 
    about_us, 
    disclaimer
)

# 3. SEO Files (seo_views.py se)
from .seo_views import (
    ads_txt, 
    robots_txt, 
    sitemap_xml
)