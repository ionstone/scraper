import asyncio
from scraper import scrape_categories, extract_product_links, extract_product_details
import json

async def main():
    base_url = "https://www.tops.co.th/en"
    categories = await scrape_categories(base_url, limit=5)
    print(categories)  # Output category URLs
    product_links = await extract_product_links(categories, limit=5)
    print(product_links)  # Output product links
    product_details = await extract_product_details(product_links)
    
    with open("extracted_products.json", "w") as file:
        json.dump(product_details, file, indent=4)
    
    print(product_details)  # Output final product details

# Run the scraping pipeline
if __name__ == "__main__":
    asyncio.run(main())
