# Web Scraping Assignment

### Task Overview
The goal of this assignment is to scrape product data from the **Tops Online** website, specifically from various categories. The extracted data will be structured in **JSON format** and will include details such as:

- Product name
- Images
- Quantities
- Barcode numbers
- Descriptions
- Prices
- Labels

---

## Data to Extract
For each product, the following details will be extracted:

- **Product Name**  
- **Product Images** (URLs of all images)  
- **Quantity** (e.g., "500g", "1L")  
- **Barcode Number** (validated as proper EAN/UPC)  
- **Product Details** (full description)  
- **Price** (numerical value + currency)  
- **Labels** (e.g., "Plant-Based," "Vegan," "Organic," "Best Seller," etc.)  

---

## Approach Used for Scraping

The web scraping process for the **Tops Online** website was designed to efficiently extract product data while handling dynamic content. The following approach was taken:

### **Technology Stack:**
- **Playwright**: Used for navigating and interacting with the website, allowing for the handling of JavaScript-rendered content.
- **BeautifulSoup**: Employed for parsing the HTML and extracting relevant product details.
- **Asyncio**: Utilized for managing asynchronous tasks, enabling concurrent page processing.

### **Scraping Workflow:**
1. **Category and Subcategory Extraction**: The script starts by scraping the main categories and their subcategories from the homepage, ensuring all relevant links are loaded.
2. **Product Link Retrieval**: Each subcategory is navigated to extract product links, employing a scrolling technique to load all products dynamically.
3. **Product Detail Extraction**: For each product link, the script loads the page, waits for the content to render, and uses **BeautifulSoup** to extract details such as name, images, quantity, barcode, price, labels, and descriptions.

### **Dynamic Content Handling:**
- Increased timeout settings and scrolling are implemented to ensure all content is fully loaded before extraction.

### **Data Validation and Cleaning:**
- Extracted data is validated for accuracy, with standardization applied to formats like pricing and barcode numbers. Missing values are handled appropriately.

### **Error Handling:**
- Robust error handling mechanisms are included, featuring retry logic for failed requests and logging for troubleshooting.

### **Rate Limiting:**
- Delays between requests are implemented to mimic human behavior and reduce the risk of IP blocking.

---


## Dependencies

To run this project, the following libraries are required:

- `playwright` - For web scraping.
- `beautifulsoup4` - For parsing HTML and extracting data.
- `lxml` - For parsing XML and HTML documents.
- `asyncio` - For handling asynchronous operations.

### Installation

Install the required libraries using the following command:

```bash
pip install -r requirements.txt
```

---

## How to Run the Script

### Clone the Repository:
```bash
git clone <repository_url>
cd web_scraper
```

### Install Dependencies:
Make sure you have **Python** installed, then install the required packages:
```bash
pip install -r requirements.txt
```

### Run the Script:
Execute the main script to start the scraping process:
```bash
python main.py
```

### Output:
The extracted product details will be saved in **`extracted_products.json`**.

---

## Challenges & Solutions

### **Challenge 1: JavaScript Loading Times**
The website relies heavily on **JavaScript** for rendering content, which can lead to delays in loading product data.

#### **Solution:**
- Increased wait times to ensure that all dynamic content loads completely before attempting to scrape data.

```python
await page.wait_for_timeout(5000)  # Increased timeout to allow content to load
```

- Implemented a method to **scroll** through the product pages, triggering the loading of additional products.

```python
async def scroll_to_load_all_products(page, scroll_delay=2):
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
```

---

## Sample Output
Below is a sample of the JSON output for the first five products scraped:

```json
{
    "OTOP": [
        {
            "productName": "(OTOP) Doikham Savoury Strawberry 30g.",
            "barCodeNumber": "8850773551115",
            "quantity": "30g",
            "price": {
                "value": 30.0,
                "currency": "THB"
            },
            "label": "OTOP Product",
            "productImages": [
                "https://assets.tops.co.th/DOIKHAM-DoikhamSavouryStrawberry30g-8850773551115-2?$JPEG$",
                "https://assets.tops.co.th/DOIKHAM-DoikhamSavouryStrawberry30g-8850773551115-1?$JPEG$"
            ],
            "productDetails": {
                "properties": "The product received may be subject to package modification and quantity from the manufacturer.\nWe reserve the right to make any changes without prior notice.\n*The images used are for advertising purposes only.",
                "ingredients": "N/A",
                "usage": "N/A",
                "description": "N/A"
            }
        },
        {
            "productName": "(OTOP) Doikham Dried Mango 140g.",
            "barCodeNumber": "8850773550262",
            "quantity": "140g",
            "price": {
                "value": 80.0,
                "currency": "THB"
            },
            "label": "OTOP Product",
            "productImages": [
                "https://assets.tops.co.th/DOIKHAM-DoikhamDriedMango140g-8850773550262-1?$JPEG$",
                "https://assets.tops.co.th/DOIKHAM-DoikhamDriedMango140g-8850773550262-4?$JPEG$"
            ],
            "productDetails": {
                "properties": "The product received may be subject to package modification and quantity from the manufacturer.\nWe reserve the right to make any changes without prior notice.\n*The images used are for advertising purposes only.",
                "ingredients": "N/A",
                "usage": "N/A",
                "description": "N/A"
            }
        }
    ]
}
```

---

### 📌 **End of Documentation**
