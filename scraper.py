import asyncio
from playwright.async_api import async_playwright
from utils import remove_duplicate_links, extract_quantity, validate_barcode, extract_price, extract_images, extract_additional_info
from bs4 import BeautifulSoup  # Import BeautifulSoup for HTML parsing

async def load_page_with_retries(page, url, wait_selector=None, max_attempts=3, load_timeout=30000):
    """Attempts to load a URL with retries and waits for a specific selector to be present."""
    backoff_time = 1  # Initialize backoff time (in seconds)

    for attempt in range(max_attempts):
        try:
            print(f"🔄 Attempting to load: {url} (Attempt {attempt + 1})")
            response = await page.goto(url, wait_until="domcontentloaded", timeout=load_timeout)
            
            if response and response.status == 200:
                print(f"✅ Successfully loaded: {url}")
                
                if wait_selector:
                    await page.wait_for_selector(wait_selector, timeout=load_timeout)
                
                return True  # Page loaded successfully

            print(f"⚠️ Response not successful for {url}: {response.status if response else 'No response'}")
        
        except Exception as error:
            print(f"⚠️ Attempt {attempt + 1} failed for {url}: {error}")

        await asyncio.sleep(backoff_time)
        backoff_time += 1  # Increase backoff time for the next attempt

    print(f"❌ Failed to load after {max_attempts} attempts: {url}")
    return False  # Page failed to load

async def scrape_categories(base_url, limit=None):
    """Scrapes category names and URLs from the given website asynchronously."""
    categories_data = {}

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        if not await load_page_with_retries(page, base_url, ".sidebar-item"):
            return {}

        category_elements = await page.locator(".sidebar-item").all()
        print(f"✅ Found {len(category_elements)} categories.")

        for category in category_elements[:limit] if limit else category_elements:
            try:
                anchor = category.locator("a")
                category_name = (await anchor.locator("span").inner_text()).strip()
                category_url = await anchor.get_attribute("href")
                
                if category_url.startswith("/"):
                    category_url = base_url + category_url[3:]

                categories_data[category_name] = await scrape_subcategories(category_url, limit)
            except Exception as e:
                print("⚠️ Error processing category:", e)

        await browser.close()

    return categories_data

async def scrape_subcategories(category_url, limit=None):
    """Extracts subcategory URLs from a category page asynchronously."""
    subcategories = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        if not await load_page_with_retries(page, category_url, ".plp-carousel__link"):
            return []

        subcategory_links = await page.locator(".plp-carousel__link").all()
        print(f"✅ Found {len(subcategory_links)} subcategories in {category_url}")

        for link in subcategory_links[:limit] if limit else subcategory_links:
            try:
                subcategory_url = await link.get_attribute("href")
                subcategories.append(subcategory_url)
            except Exception as e:
                print("⚠️ Error extracting subcategory:", e)

        await browser.close()

    return subcategories

async def scroll_to_load_all_products(page, scroll_delay=2):
    """Scrolls down the page to ensure all products are loaded."""
    last_height = await page.evaluate("document.body.scrollHeight")
    
    while True:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        await asyncio.sleep(scroll_delay)
        
        new_height = await page.evaluate("document.body.scrollHeight")
        
        if new_height == last_height:
            print("✅ All products loaded successfully!")
            break
        
        last_height = new_height

async def extract_product_links(subcategories, limit=None):
    """Extracts product links from subcategory pages."""
    products = {}

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        for category, subcategory_list in subcategories.items():
            products[category] = []
            for subcategory_url in subcategory_list:
                if not await load_page_with_retries(page, subcategory_url, ".product-item-inner-wrap"):
                    continue
                await scroll_to_load_all_products(page)
                product_elements = await page.locator(".product-item-inner-wrap").all()
                print(f"✅ Found {len(product_elements)} products in {subcategory_url}")

                for product in product_elements[:limit] if limit else product_elements:
                    try:
                        product_url = await product.get_attribute("href")
                        products[category].append(product_url)
                    except Exception as e:
                        print("⚠️ Error extracting product link:", e)

        await browser.close()

    return products

async def extract_product_details(products):
    """Extract detailed product information from product pages asynchronously, removing duplicates based on name and SKU."""
    product_data = {}
    unique_products = {}

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        for category, product_list in products.items():
            product_data[category] = []

            product_list = remove_duplicate_links({'dummy': product_list})['dummy']  # Remove duplicates

            for product_url in product_list:
                try:
                    if not await load_page_with_retries(page, product_url, ".product-Details-page-root"):
                        print(f"⚠️ Failed to load product page: {product_url}")
                        continue
                    
                    content = await page.content()
                    soup = BeautifulSoup(content, "lxml")

                    product_container = soup.select_one(".product-Details-page-root")
                    if not product_container:
                        print(f"⚠️ Product details not found for URL: {product_url}")
                        continue
                    
                    product_name = product_container.get("data-product-name", "N/A")
                    barcode = validate_barcode(product_container.get("data-product-id", "N/A")) or "N/A"

                    unique_id = (product_name, barcode)

                    if unique_id not in unique_products:
                        product_details = {
                            "productName": product_name,
                            "barCodeNumber": barcode,
                            "quantity": extract_quantity(product_name),
                            "price": extract_price(product_container),
                            "label": product_container.get("data-product-badge-label", "N/A"),
                            "productImages": extract_images(product_container),
                            "productDetails": extract_additional_info(product_container)
                        }

                        product_data[category].append(product_details)
                        unique_products[unique_id] = product_details
                    else:
                        print(f"⚠️ Duplicate product found: {unique_id}")

                except Exception as e:
                    print(f"❌ Error extracting product details for {product_url}: {e}")

        await browser.close()

    return product_data
