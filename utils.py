import re
from bs4 import BeautifulSoup

def remove_duplicate_links(products):
    """Removes duplicate product links from the product list."""
    unique_products = {}
    duplicates = {}

    for category, links in products.items():
        unique_products[category] = []
        for link in links:
            if link not in unique_products[category]:
                unique_products[category].append(link)
            else:
                if link in duplicates:
                    duplicates[link] += 1
                else:
                    duplicates[link] = 2  # Count this instance as a duplicate

    for link, count in duplicates.items():
        print(f"⚠️ Removed duplicate link: {link} (Count: {count})")

    return unique_products

def extract_price(container):
    """Extracts product price from the container."""
    price = container.get("data-product-price-new", "N/A")
    try:
        return {"value": float(price), "currency": "THB"} if price != "N/A" else "N/A"
    except ValueError:
        return "N/A"

def extract_images(container):
    """Extracts product images from the container."""
    img_container = container.select_one(".product-Details-images")
    img_tags = img_container.find_all("img") if img_container else []
    return list(set(img["src"] for img in img_tags if "src" in img.attrs))

def extract_additional_info(container):
    """Extracts additional product information."""
    return {
        "properties": extract_paragraphs_with_newlines(container.select_one(".accordion-property")),
        "ingredients": extract_paragraphs_with_newlines(container.select_one(".accordion-ingredient")),
        "usage": extract_paragraphs_with_newlines(container.select_one(".accordion-direction")),
        "description": extract_description(container)
    }

def extract_paragraphs_with_newlines(container):
    """Extracts text from paragraphs within a container."""
    if container:
        return "\n".join(p.get_text(strip=True) for p in container.find_all("p"))
    return "N/A"

def extract_description(container):
    """Extracts the description image or video."""
    description_link = "N/A"
    
    description_img = container.select_one(".accordion-item-description img")
    if description_img and "src" in description_img.attrs:
        description_link = description_img["src"]
    
    description_video = container.select_one(".youtube-embed-wrapper iframe")
    if description_video and "src" in description_video.attrs:
        description_link = f'https:{description_video["src"]}'

    return description_link

def extract_quantity(product_name):
    """Extracts the quantity from a product name."""
    quantity_pattern = r"(\d+\.?\d*)\s*(kg|g|ltr|ml|Kg|G|Ltr|Ml|KG|LTR|ML)?"
    match = re.search(quantity_pattern, product_name, re.IGNORECASE)

    if match and match.group(2):
        return f"{match.group(1)}{match.group(2).lower()}"
    
    return "N/A"

def validate_barcode(barcode):
    """Validates if the barcode is a proper EAN-13 or UPC-A."""
    cleaned_barcode = re.sub(r'\D', '', barcode)
    return cleaned_barcode if len(cleaned_barcode) in [12, 13] else None
