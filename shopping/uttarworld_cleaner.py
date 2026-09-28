from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

def clean_amazon_affiliate_link(raw_url, tracking_id="uttarworld202-21"):
    """
    Amazon ke messy ya multi-parameter links ko clean karke 
    sirf base product URL aur designated tracking tag retain karta hai.
    """
    if not raw_url or "amazon" not in raw_url:
        return raw_url
        
    parsed_url = urlparse(raw_url)
    
    # Clean up the path: Amazon products ke liye path usually /dp/ASIN ya /gp/product/ASIN hota hai
    path_parts = parsed_url.path.split('/')
    clean_path = ""
    
    # ASIN nikalne ki koshish karte hain
    asin = None
    for i, part in enumerate(path_parts):
        if part in ['dp', 'gp'] and i + 1 < len(path_parts):
            # Agla part ASIN ho sakta hai ya product name ke baad ho sakta hai
            if part == 'dp' and i + 1 < len(path_parts):
                asin = path_parts[i+1]
            elif part == 'gp' and i + 2 < len(path_parts) and path_parts[i+1] == 'product':
                asin = path_parts[i+2]
                
    if asin:
        # Standard clean path format bana lo
        clean_path = f"/dp/{asin}"
    else:
        # Agar ASIN standard format mein na mile toh original path ko thoda sanitize kar do
        clean_path = parsed_url.path
        
    # Query parameters ko parse karo
    query_params = dict(parse_qsl(parsed_url.query))
    
    # Sirf zaroori parameters rakho (jaise tag), baaki sab uda do!
    new_query_params = {}
    if tracking_id:
        new_query_params['tag'] = tracking_id
        
    # Agar koi aur zaroori parameter rakhna ho toh yahan handle kar sakte hain
    
    encoded_query = urlencode(new_query_params)
    
    # Final clean URL assemble karo
    clean_tuple = (
        parsed_url.scheme or 'https',
        parsed_url.netloc or 'www.amazon.in',
        clean_path,
        '', # params
        encoded_query,
        ''  # fragment
    )
    
    return urlunparse(clean_tuple)

# --- Testing Example ---
if __name__ == "__main__":
    messy_link = "https://www.amazon.in/Amazon-Brand-Vedaka-Extra-Strong/dp/B07PWG619Y/ref=sr_1_1?crid=23XYZ&dib=eyJ2IjoiMSJ9&keywords=tea&qid=123456&rnid=123&s=grocery&sprefix=tea%2Caps%2C200&sr=1-1&tag=wrongtag-21&ascsubtag=12345"
    print("Cleaned Link:", clean_amazon_affiliate_link(messy_link, "uttarworld202-21"))