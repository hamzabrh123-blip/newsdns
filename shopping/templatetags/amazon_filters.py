from django import template
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

register = template.Library()

@register.filter(name='clean_amazon')
def clean_amazon_affiliate_link(raw_url, tracking_id="uttarworld202-21"):
    if not raw_url or "amazon" not in raw_url:
        return raw_url
        
    parsed_url = urlparse(raw_url)
    path_parts = parsed_url.path.split('/')
    
    asin = None
    for i, part in enumerate(path_parts):
        if part == 'dp' and i + 1 < len(path_parts):
            asin = path_parts[i+1]
            break
        elif part == 'gp' and i + 2 < len(path_parts) and path_parts[i+1] == 'product':
            asin = path_parts[i+2]
            break
            
    clean_path = f"/dp/{asin}" if asin else parsed_url.path
    
    # Sirf zaroori tracking tag rakho, baaki saara junk parameters hata do
    new_query_params = {'tag': tracking_id}
    encoded_query = urlencode(new_query_params)
    
    clean_tuple = (
        parsed_url.scheme or 'https',
        parsed_url.netloc or 'www.amazon.in',
        clean_path,
        '',
        encoded_query,
        ''
    )
    return urlunparse(clean_tuple)