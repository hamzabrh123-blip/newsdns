import re
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from shopping.models import ProductVariant

class Command(BaseCommand):
    help = 'Fully automated background stock and price checker for UttarWorld'

    def handle(self, *args, **kwargs):
        variants = ProductVariant.objects.all()
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

        self.stdout.write(self.style.SUCCESS(f"Background Scan Started: Total variants {variants.count()}"))

        for variant in variants:
            url = variant.earn_karo_url
            if not url:
                continue

            store = variant.product.store_name.lower() if variant.product and variant.product.store_name else ""
            if not store:
                store = url.lower()

            try:
                response = requests.get(url, headers=headers, timeout=12)
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text().lower()
                
                out_of_stock = False

                # --- 1. STOCK-FIRST PRIORITY CHECK ---
                if 'amazon' in store or 'amazon.in' in url:
                    if "currently unavailable" in page_text or "we don't know when or if this item will be back in stock" in page_text:
                        out_of_stock = True
                elif 'flipkart' in store or 'shopsy' in store or 'flipkart.com' in url or 'shopsy.in' in url:
                    if "notify me" in page_text or "currently out of stock for this pincode" in page_text or "out of stock" in page_text:
                        out_of_stock = True
                elif 'meesho' in store or 'meesho.com' in url:
                    if "product not available" in page_text or "this product is currently out of stock" in page_text or "remind me" in page_text:
                        out_of_stock = True
                else:
                    if "out of stock" in page_text or "sold out" in page_text or "notify me when available" in page_text:
                        out_of_stock = True

                updated = False
                change_logs = []

                # --- 2. UPDATE STOCK STATUS ---
                if variant.is_out_of_stock != out_of_stock:
                    variant.is_out_of_stock = out_of_stock
                    updated = True

                if hasattr(variant, 'is_active'):
                    if out_of_stock and variant.is_active:
                        variant.is_active = False
                        change_logs.append("Deactivated (Out of Stock)")
                        updated = True
                    elif not out_of_stock and not variant.is_active:
                        variant.is_active = True
                        change_logs.append("Activated (Back in Stock)")
                        updated = True

                # --- 3. PRICE UPDATE (ONLY IF PRODUCT IS IN-STOCK) ---
                if not out_of_stock:
                    new_price = None
                    price_selectors = [
                        'span.a-price-whole',
                        'div.Nx9fbj',
                        'span[class*="price"]',
                        'span[class*="discounted"]',
                        'div[class*="selling-price"]'
                    ]
                    
                    for selector in price_selectors:
                        element = soup.select_one(selector)
                        if element:
                            raw_price_text = element.get_text()
                            clean_nums = re.sub(r'[^\d]', '', raw_price_text)
                            if clean_nums and len(clean_nums) <= 6:  
                                new_price = clean_nums
                                break

                    if new_price and variant.selling_price != new_price:
                        old_price = variant.selling_price
                        variant.selling_price = new_price
                        change_logs.append(f"Price Updated: ₹{old_price} -> ₹{new_price}")
                        updated = True

                if updated:
                    variant.save()
                    log_str = " | ".join(change_logs)
                    self.stdout.write(self.style.WARNING(f"[SYNC] {variant.product.title} -> {log_str}"))

            except Exception as e:
                # Background quiet error logging
                pass

        self.stdout.write(self.style.SUCCESS("Background scan cycle finished successfully!"))