# Web Scraping in Python

Web scraping is the automated process of extracting data from websites.  
It involves fetching web pages and parsing their content to collect specific  
information. Web scraping transforms unstructured web data into structured  
formats suitable for analysis, storage, or further processing.  

## What is Web Scraping?

Web scraping enables programmatic access to web content that would otherwise  
require manual browsing and copying. A web scraper sends HTTP requests to  
target URLs, receives HTML responses, and extracts desired data elements  
using various parsing techniques.  

Common use cases for web scraping include:  

- **Price monitoring**: Tracking product prices across e-commerce sites  
- **Market research**: Gathering competitor information and industry trends  
- **Data aggregation**: Collecting data from multiple sources for analysis  
- **Content indexing**: Building search engines or content databases  
- **Lead generation**: Extracting contact information from directories  
- **Academic research**: Gathering data for studies and publications  
- **News monitoring**: Aggregating articles and tracking topics  
- **Real estate analysis**: Collecting property listings and prices  

Benefits of web scraping include automation of repetitive data collection,  
access to large datasets, real-time data updates, and competitive intelligence.  
However, risks include legal issues, website blocking, data quality problems,  
and maintenance overhead when websites change their structure.  

---

## Legal and Ethical Considerations

Web scraping operates in a complex legal landscape. Before scraping any  
website, consider these important factors:  

### Respecting robots.txt

The robots.txt file tells web crawlers which parts of a site they can access.  
Located at the root of a domain (e.g., https://example.com/robots.txt), this  
file specifies allowed and disallowed paths. Always check and respect these  
directives.  

```python
import urllib.robotparser

rp = urllib.robotparser.RobotFileParser()
rp.set_url("https://example.com/robots.txt")
rp.read()

# Check if scraping a specific path is allowed
can_fetch = rp.can_fetch("*", "/some-page")
print(f"Allowed to scrape: {can_fetch}")
```

### Avoiding Server Overload

Sending too many requests too quickly can overwhelm servers and may be  
considered a denial-of-service attack. Implement rate limiting in your  
scrapers:  

- Add delays between requests (1-5 seconds minimum)  
- Respect Crawl-delay directives in robots.txt  
- Distribute requests over time for large-scale scraping  
- Consider scraping during off-peak hours  

### Terms of Service

Many websites explicitly prohibit scraping in their Terms of Service.  
Violating these terms could result in legal action, IP blocking, or  
account termination. Read and understand the ToS before scraping.  

### Data Privacy Laws

Regulations like GDPR (Europe), CCPA (California), and others restrict how  
personal data can be collected and processed. When scraping:  

- Avoid collecting personal information without consent  
- Implement data minimization principles  
- Ensure proper data storage and security  
- Consider the purpose and necessity of data collection  

### Best Practices for Ethical Scraping

- Identify your scraper with a descriptive User-Agent  
- Cache responses to avoid redundant requests  
- Use official APIs when available  
- Only scrape publicly available information  
- Store data securely and use it responsibly  
- Consider contacting website owners for permission  

---

## Prerequisites

### Essential Python Libraries

Install the required libraries using pip:  

```bash
pip install requests beautifulsoup4 lxml selenium scrapy aiohttp pandas
```

**Requests** is the standard library for making HTTP requests. It provides  
a simple interface for fetching web pages.  

```bash
pip install requests
```

**BeautifulSoup** parses HTML and XML documents, providing methods to  
navigate and search the parse tree. Combined with lxml parser, it offers  
fast and reliable parsing.  

```bash
pip install beautifulsoup4 lxml
```

**Selenium** automates web browsers, essential for scraping JavaScript-  
rendered content and interacting with dynamic pages.  

```bash
pip install selenium
```

You also need a browser driver (e.g., ChromeDriver for Chrome). With  
Selenium 4.6+, drivers can be managed automatically using the included  
Selenium Manager.  

**Scrapy** is a comprehensive web crawling framework with built-in  
features for handling requests, following links, and exporting data.  

```bash
pip install scrapy
```

**aiohttp** enables asynchronous HTTP requests for efficient concurrent  
scraping.  

```bash
pip install aiohttp
```

---

## Basic Concepts

### HTML Structure

HTML documents consist of nested elements forming a tree structure.  
Understanding this structure is essential for locating target data:  

```html
<!DOCTYPE html>
<html>
<head>
    <title>Example Page</title>
</head>
<body>
    <div class="container">
        <h1 id="main-title">Welcome</h1>
        <ul class="items">
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
    </div>
</body>
</html>
```

Elements have tags (`div`, `h1`, `ul`), attributes (`class`, `id`), and  
content (text or nested elements).  

### CSS Selectors

CSS selectors identify elements based on their attributes and position:  

| Selector | Description | Example |
|----------|-------------|---------|
| `tag` | Select by tag name | `div` selects all divs |
| `.class` | Select by class | `.items` selects elements with class "items" |
| `#id` | Select by ID | `#main-title` selects element with ID "main-title" |
| `tag.class` | Combined selector | `ul.items` selects ul with class "items" |
| `parent child` | Descendant selector | `div li` selects li inside div |
| `parent > child` | Direct child | `ul > li` selects direct li children of ul |
| `[attr=value]` | Attribute selector | `[href="/page"]` selects by attribute |

### XPath

XPath is a query language for selecting nodes in XML/HTML documents:  

| XPath | Description |
|-------|-------------|
| `//div` | Select all div elements |
| `//div[@class="container"]` | Div with specific class |
| `//ul/li` | Li elements that are children of ul |
| `//h1/text()` | Text content of h1 elements |
| `//a/@href` | Href attribute of anchor elements |
| `//div[contains(@class, "item")]` | Div with class containing "item" |

### HTTP Requests

Web scraping relies on HTTP methods:  

- **GET**: Retrieve data from a URL  
- **POST**: Send data to a server (forms, login)  
- **Headers**: Metadata like User-Agent, cookies, content type  
- **Status Codes**: 200 (success), 404 (not found), 403 (forbidden), etc.  

### Common Challenges

- **Anti-scraping measures**: CAPTCHAs, IP blocking, honeypot traps  
- **JavaScript rendering**: Content loaded dynamically via JavaScript  
- **Rate limiting**: Servers limiting request frequency  
- **Session management**: Maintaining login state across requests  
- **Changing layouts**: Website redesigns breaking scrapers  
- **Error handling**: Network issues, timeouts, malformed HTML  

---

## Practical Examples

The following examples demonstrate various web scraping techniques using  
safe, public websites. Each example includes complete code, explanations,  
and best practices.  

---

### Scraping Static HTML Pages

This example fetches a simple webpage and extracts basic information.  
We use the httpbin.org service, which provides test endpoints.  

```python
import requests
from bs4 import BeautifulSoup

# Define target URL and headers
url = "https://httpbin.org/html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36"
}

# Send GET request with custom headers
response = requests.get(url, headers=headers, timeout=10)

# Check if request was successful
if response.status_code == 200:
    # Parse HTML content
    soup = BeautifulSoup(response.text, "lxml")
    
    # Extract the heading
    heading = soup.find("h1")
    if heading:
        print(f"Heading: {heading.get_text()}")
    
    # Extract all paragraphs
    paragraphs = soup.find_all("p")
    for i, p in enumerate(paragraphs, 1):
        print(f"Paragraph {i}: {p.get_text()[:50]}...")
else:
    print(f"Request failed with status: {response.status_code}")
```

The code sends an HTTP GET request with a browser-like User-Agent header  
to avoid being blocked. BeautifulSoup parses the HTML response, and we  
use find() for single elements and find_all() for multiple elements.  
The get_text() method extracts text content from elements.  

Sample output:  

```
Heading: Herman Melville - Moby-Dick
Paragraph 1: Availing himself of the mild, summer-cool weat...
```

**Best practices demonstrated**:  
- Using a realistic User-Agent to mimic browser requests  
- Setting a timeout to prevent hanging on slow responses  
- Checking status codes before processing  
- Handling potential None values when elements are not found  

**Improvements**: Add retry logic for failed requests, implement  
exponential backoff, cache responses to avoid redundant requests.  

---

### Extracting Data from Tables

Tables are common on websites for presenting structured data. This example  
scrapes a table from the W3Schools HTML tables reference page.  

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.w3schools.com/html/html_tables.asp"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36"
}

response = requests.get(url, headers=headers, timeout=10)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "lxml")
    
    # Find the first table on the page
    table = soup.find("table", class_="ws-table-all")
    
    if table:
        # Extract headers from the first row
        headers_row = table.find("tr")
        headers_list = [th.get_text(strip=True) 
                       for th in headers_row.find_all(["th", "td"])]
        
        # Extract data rows
        rows = []
        for tr in table.find_all("tr")[1:]:  # Skip header row
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if cells:
                rows.append(cells)
        
        # Create DataFrame for easy manipulation
        df = pd.DataFrame(rows, columns=headers_list[:len(rows[0])] 
                         if rows else headers_list)
        print(df.to_string())
    else:
        print("Table not found")
else:
    print(f"Request failed: {response.status_code}")
```

The code locates the target table by its class attribute, extracts header  
cells, then iterates through data rows collecting cell contents. Using  
pandas DataFrame provides convenient data manipulation and export options.  
The strip=True parameter removes whitespace from extracted text.  

Sample output:  

```
     Tag                        Description
0   <table>     Defines a table
1   <th>        Defines a header cell in a table
2   <tr>        Defines a row in a table
3   <td>        Defines a cell in a table
```

**Improvements**: Handle tables with rowspan/colspan attributes, implement  
error handling for malformed tables, add support for multiple tables.  

---

### Extracting Data from Lists

This example demonstrates extracting structured data from HTML lists,  
using the official Python documentation page.  

```python
import requests
from bs4 import BeautifulSoup

url = "https://docs.python.org/3/library/functions.html"
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; PythonScraper/1.0)"
}

response = requests.get(url, headers=headers, timeout=15)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "lxml")
    
    # Find all function definitions in the documentation
    functions = soup.find_all("dl", class_="py function")
    
    extracted_functions = []
    for func in functions[:10]:  # Limit to first 10
        # Extract function signature
        dt = func.find("dt")
        if dt:
            func_id = dt.get("id", "unknown")
            signature = dt.get_text(strip=True)
            
            # Extract description from dd element
            dd = func.find("dd")
            description = ""
            if dd:
                first_p = dd.find("p")
                if first_p:
                    description = first_p.get_text(strip=True)[:100]
            
            extracted_functions.append({
                "id": func_id,
                "signature": signature[:60],
                "description": description
            })
    
    # Display extracted data
    for func in extracted_functions:
        print(f"\n{func['id']}:")
        print(f"  Signature: {func['signature']}")
        print(f"  Description: {func['description']}...")
else:
    print(f"Request failed: {response.status_code}")
```

This code navigates the Python documentation structure, finding function  
definitions marked with specific CSS classes. It extracts the function  
ID, signature, and first paragraph of the description. Dictionary storage  
enables easy export to JSON or CSV formats.  

Sample output:  

```
abs:
  Signature: abs(x)
  Description: Return the absolute value of a number...

aiter:
  Signature: aiter(async_iterable)
  Description: Return an asynchronous iterator...
```

**Best practices demonstrated**:  
- Using descriptive User-Agent identifying the scraper  
- Limiting results to avoid excessive data collection  
- Graceful handling of missing elements  

---

### Handling Pagination

Many websites split content across multiple pages. This example shows  
how to navigate through paginated content using the JSONPlaceholder API,  
simulating pagination with limit and offset parameters.  

```python
import requests
import time

base_url = "https://jsonplaceholder.typicode.com/posts"
headers = {"User-Agent": "PaginationScraper/1.0"}

all_posts = []
page = 1
per_page = 10
max_pages = 5

while page <= max_pages:
    # Calculate offset for pagination
    start = (page - 1) * per_page
    
    params = {
        "_start": start,
        "_limit": per_page
    }
    
    print(f"Fetching page {page}...")
    response = requests.get(base_url, headers=headers, 
                           params=params, timeout=10)
    
    if response.status_code == 200:
        posts = response.json()
        
        if not posts:  # No more data
            print("No more posts found")
            break
        
        all_posts.extend(posts)
        print(f"  Retrieved {len(posts)} posts")
        
        page += 1
        
        # Rate limiting: wait between requests
        time.sleep(1)
    else:
        print(f"Error: {response.status_code}")
        break

print(f"\nTotal posts collected: {len(all_posts)}")

# Display sample of collected data
for post in all_posts[:3]:
    print(f"\nPost {post['id']}: {post['title'][:50]}...")
```

The code implements a pagination loop that increments the offset with each  
request. It checks for empty responses to detect the end of available data.  
A one-second delay between requests prevents overwhelming the server.  
All results accumulate in a single list for further processing.  

Sample output:  

```
Fetching page 1...
  Retrieved 10 posts
Fetching page 2...
  Retrieved 10 posts
Fetching page 3...
  Retrieved 10 posts
Fetching page 4...
  Retrieved 10 posts
Fetching page 5...
  Retrieved 10 posts

Total posts collected: 50

Post 1: sunt aut facere repellat provident occaecati ...
Post 2: qui est esse...
Post 3: ea molestias quasi exercitationem repellat qui ...
```

**Improvements**: Implement parallel fetching with rate limiting, add  
resume capability for interrupted scrapes, handle next-page links  
for sites without offset-based pagination.  

---

### Dealing with Dynamic Content Using Selenium

Some websites load content via JavaScript after the initial page load.  
Selenium controls a real browser to render such pages. This example  
demonstrates waiting for dynamic content.  

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run without GUI
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 Chrome/91.0.4472.124"
)

# Initialize the driver (Selenium Manager handles driver automatically)
driver = webdriver.Chrome(options=chrome_options)

try:
    # Navigate to a page with dynamic content
    url = "https://quotes.toscrape.com/js/"
    driver.get(url)
    
    # Wait for dynamic content to load (up to 10 seconds)
    wait = WebDriverWait(driver, 10)
    quotes_container = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "quote"))
    )
    
    # Extract quotes after JavaScript has rendered them
    quotes = driver.find_elements(By.CLASS_NAME, "quote")
    
    for quote in quotes[:5]:
        text_elem = quote.find_element(By.CLASS_NAME, "text")
        author_elem = quote.find_element(By.CLASS_NAME, "author")
        
        text = text_elem.text
        author = author_elem.text
        
        print(f'"{text[:60]}..."')
        print(f"  - {author}\n")
    
    # Take a screenshot for debugging
    driver.save_screenshot("/tmp/selenium_screenshot.png")
    print("Screenshot saved to /tmp/selenium_screenshot.png")

finally:
    # Always close the browser
    driver.quit()
```

The code initializes a headless Chrome browser with Selenium, navigating  
to a JavaScript-rendered page. WebDriverWait ensures the script waits  
until dynamic content is present before extraction. The headless mode  
runs without a visible browser window, suitable for servers.  

Sample output:  

```
"The world as we have created it is a process of our think..."
  - Albert Einstein

"It is our choices, Harry, that show what we truly are, far..."
  - J.K. Rowling

"There are only two ways to live your life. One is as thoug..."
  - Albert Einstein
```

**Best practices demonstrated**:  
- Using headless mode for efficiency  
- Explicit waits instead of arbitrary sleep calls  
- Proper cleanup with try/finally block  
- Custom User-Agent for the browser  

**Alternatives**: Consider using Playwright, Puppeteer (via pyppeteer),  
or requests-html for JavaScript rendering.  

---

### Logging In and Scraping Authenticated Pages

Some data requires authentication. This example demonstrates session-based  
login using the Quotes to Scrape practice site.  

```python
import requests
from bs4 import BeautifulSoup

# Create a session to maintain cookies
session = requests.Session()

# Set common headers
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36"
})

# Step 1: Get the login page to obtain CSRF token
login_url = "https://quotes.toscrape.com/login"
response = session.get(login_url, timeout=10)

if response.status_code != 200:
    print(f"Failed to load login page: {response.status_code}")
    exit(1)

# Extract CSRF token from the form
soup = BeautifulSoup(response.text, "lxml")
csrf_input = soup.find("input", {"name": "csrf_token"})
csrf_token = csrf_input["value"] if csrf_input else ""

print(f"CSRF token obtained: {csrf_token[:20]}...")

# Step 2: Submit login form
login_data = {
    "csrf_token": csrf_token,
    "username": "demo",  # Any username works on this demo site
    "password": "demo"   # Any password works on this demo site
}

response = session.post(login_url, data=login_data, timeout=10)

# Check if login was successful by looking for logout link
if "Logout" in response.text:
    print("Login successful!")
    
    # Step 3: Access authenticated content
    soup = BeautifulSoup(response.text, "lxml")
    
    # Extract quotes from the authenticated page
    quotes = soup.find_all("div", class_="quote")
    
    print(f"\nFound {len(quotes)} quotes:")
    for quote in quotes[:3]:
        text = quote.find("span", class_="text")
        author = quote.find("small", class_="author")
        
        if text and author:
            print(f'\n"{text.get_text()[:50]}..."')
            print(f"  - {author.get_text()}")
else:
    print("Login failed!")

# Session automatically handles cookies for subsequent requests
```

The code uses a requests Session object to maintain cookies across  
requests. It first fetches the login page to extract any CSRF tokens,  
then submits credentials via POST. The session preserves authentication  
state for accessing protected pages.  

Sample output:  

```
CSRF token obtained: IjQ2ZDQ4ZTI1NTJjZT...
Login successful!

Found 10 quotes:

"The world as we have created it is a process of..."
  - Albert Einstein

"It is our choices, Harry, that show what we trul..."
  - J.K. Rowling
```

**Security notes**:  
- Never hardcode real credentials in scripts  
- Use environment variables or secure credential storage  
- Be aware of legal implications of accessing authenticated content  

---

### Building a Simple Spider with Scrapy

Scrapy is a powerful framework for building web spiders. This example  
creates a spider to crawl the Quotes to Scrape website.  

First, create a new Scrapy project:  

```bash
scrapy startproject quotespider
cd quotespider
```

Create a spider file at `quotespider/spiders/quotes_spider.py`:  

```python
import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]
    
    custom_settings = {
        "DOWNLOAD_DELAY": 1,  # Be polite: 1 second between requests
        "USER_AGENT": "QuotesSpider/1.0 (+https://example.com/bot)",
        "ROBOTSTXT_OBEY": True,
    }
    
    def parse(self, response):
        # Extract quotes from the current page
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(),
                "author": quote.css("small.author::text").get(),
                "tags": quote.css("div.tags a.tag::text").getall(),
            }
        
        # Follow pagination links
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
```

Run the spider and save results to JSON:  

```bash
scrapy crawl quotes -o quotes.json
```

The spider defines start URLs and a parse method that extracts data  
using CSS selectors. The yield statement returns extracted items and  
response.follow handles pagination automatically. Custom settings  
configure polite scraping behavior.  

Sample output (quotes.json):  

```json
[
  {
    "text": "\u201cThe world as we have created it...\u201d",
    "author": "Albert Einstein",
    "tags": ["change", "deep-thoughts", "thinking", "world"]
  },
  {
    "text": "\u201cIt is our choices, Harry...\u201d",
    "author": "J.K. Rowling",
    "tags": ["abilities", "choices"]
  }
]
```

**Scrapy advantages**:  
- Built-in handling for concurrent requests  
- Automatic retry and error handling  
- Export to multiple formats (JSON, CSV, XML)  
- Middleware for customizing request/response processing  
- Item pipelines for data processing  

---

### Scraping Images and Files

This example downloads images from a webpage, demonstrating file  
handling and binary content.  

```python
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import time

# Create directory for downloaded images
output_dir = "/tmp/scraped_images"
os.makedirs(output_dir, exist_ok=True)

# Target page with images
url = "https://httpbin.org/image"
headers = {
    "User-Agent": "ImageScraper/1.0",
    "Accept": "image/png"
}

# Download a sample image
response = requests.get(url, headers=headers, timeout=15)

if response.status_code == 200:
    # Save the image
    filename = os.path.join(output_dir, "sample_image.png")
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"Downloaded: {filename}")
    print(f"File size: {len(response.content)} bytes")

# Example: Scraping multiple images from a page
def download_images_from_page(page_url, output_folder, max_images=5):
    """Download images from a webpage."""
    session = requests.Session()
    session.headers.update({"User-Agent": "ImageScraper/1.0"})
    
    response = session.get(page_url, timeout=15)
    
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, "lxml")
    images = soup.find_all("img")
    
    downloaded = 0
    for img in images:
        if downloaded >= max_images:
            break
        
        # Get image URL (handle relative URLs)
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        
        img_url = urljoin(page_url, src)
        
        # Skip data URLs
        if img_url.startswith("data:"):
            continue
        
        try:
            # Download image
            img_response = session.get(img_url, timeout=10)
            
            if img_response.status_code == 200:
                # Generate filename from URL
                img_name = os.path.basename(img_url.split("?")[0])
                if not img_name:
                    img_name = f"image_{downloaded}.jpg"
                
                filepath = os.path.join(output_folder, img_name)
                
                with open(filepath, "wb") as f:
                    f.write(img_response.content)
                
                print(f"Downloaded: {img_name} ({len(img_response.content)} bytes)")
                downloaded += 1
                
                # Rate limiting
                time.sleep(0.5)
        
        except requests.RequestException as e:
            print(f"Failed to download {img_url}: {e}")
    
    print(f"\nTotal images downloaded: {downloaded}")

# Usage example with a public page
download_images_from_page(
    "https://www.python.org/",
    output_dir,
    max_images=3
)
```

The code demonstrates downloading binary content using response.content  
instead of response.text. urljoin handles relative URLs correctly.  
The function iterates through img tags, extracting src attributes and  
downloading each image with proper error handling.  

Sample output:  

```
Downloaded: /tmp/scraped_images/sample_image.png
File size: 8090 bytes
Downloaded: python-logo.png (12150 bytes)
Downloaded: python-powered.png (4521 bytes)
Downloaded: psf-logo.png (8234 bytes)

Total images downloaded: 3
```

**Best practices demonstrated**:  
- Creating output directories safely with os.makedirs  
- Using binary mode ("wb") for writing files  
- Handling relative URLs with urljoin  
- Rate limiting between downloads  

---

### Asynchronous Scraping for Efficiency

Asynchronous scraping dramatically improves performance when fetching  
many pages. This example uses aiohttp and asyncio.  

```python
import asyncio
import aiohttp
import time

async def fetch_page(session, url):
    """Fetch a single page asynchronously."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                text = await response.text()
                return {"url": url, "length": len(text), "status": "success"}
            else:
                return {"url": url, "status": f"error_{response.status}"}
    except asyncio.TimeoutError:
        return {"url": url, "status": "timeout"}
    except Exception as e:
        return {"url": url, "status": f"error: {str(e)}"}

async def scrape_multiple(urls, max_concurrent=5):
    """Scrape multiple URLs with concurrency limit."""
    # Semaphore limits concurrent connections
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_with_semaphore(session, url):
        async with semaphore:
            return await fetch_page(session, url)
    
    headers = {"User-Agent": "AsyncScraper/1.0"}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [fetch_with_semaphore(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

# List of URLs to scrape
urls = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/get",
    "https://httpbin.org/headers",
    "https://httpbin.org/ip",
    "https://httpbin.org/user-agent",
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://jsonplaceholder.typicode.com/posts/2",
    "https://jsonplaceholder.typicode.com/users/1",
]

# Run the async scraper
print(f"Scraping {len(urls)} URLs asynchronously...")
start_time = time.time()

results = asyncio.run(scrape_multiple(urls, max_concurrent=3))

elapsed = time.time() - start_time
print(f"\nCompleted in {elapsed:.2f} seconds")

# Display results
print("\nResults:")
for result in results:
    status = result["status"]
    length = result.get("length", "N/A")
    print(f"  {result['url'][-30:]:30} - {status} ({length} bytes)")

# Compare with sequential timing estimate
print(f"\nSequential would take ~{len(urls)} seconds minimum")
print(f"Async speedup: ~{len(urls)/elapsed:.1f}x faster")
```

The code uses asyncio.Semaphore to limit concurrent connections,  
preventing server overload. aiohttp.ClientSession manages connections  
efficiently. asyncio.gather runs all fetch tasks concurrently within  
the semaphore limit.  

Sample output:  

```
Scraping 8 URLs asynchronously...

Completed in 1.45 seconds

Results:
  /delay/1                       - success (308 bytes)
  /get                           - success (391 bytes)
  /headers                       - success (234 bytes)
  /ip                            - success (31 bytes)
  /user-agent                    - success (45 bytes)
  ypicode.com/posts/1            - success (292 bytes)
  ypicode.com/posts/2            - success (252 bytes)
  ypicode.com/users/1            - success (509 bytes)

Sequential would take ~8 seconds minimum
Async speedup: ~5.5x faster
```

**Key concepts**:  
- async/await syntax for non-blocking operations  
- Semaphore for rate limiting concurrent requests  
- ClientSession for connection pooling  
- asyncio.gather for concurrent task execution  

---

### Integrating with APIs as a Hybrid Approach

When available, APIs provide more reliable data access than scraping.  
This example combines API calls with HTML parsing as a fallback.  

```python
import requests
from bs4 import BeautifulSoup
import json

class HybridScraper:
    """Scraper that prefers APIs but falls back to HTML parsing."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "HybridScraper/1.0",
            "Accept": "application/json, text/html"
        })
    
    def get_github_repo_info(self, owner, repo):
        """Get repository info via API first, fallback to scraping."""
        
        # Try API first (GitHub provides a public API)
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        try:
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "api",
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "stars": data.get("stargazers_count"),
                    "forks": data.get("forks_count"),
                    "language": data.get("language"),
                    "url": data.get("html_url")
                }
            elif response.status_code == 403:
                print("API rate limited, falling back to HTML scraping...")
                return self._scrape_github_page(owner, repo)
            else:
                print(f"API error {response.status_code}, trying HTML...")
                return self._scrape_github_page(owner, repo)
                
        except requests.RequestException as e:
            print(f"API request failed: {e}, trying HTML...")
            return self._scrape_github_page(owner, repo)
    
    def _scrape_github_page(self, owner, repo):
        """Fallback: scrape the HTML page directly."""
        html_url = f"https://github.com/{owner}/{repo}"
        
        try:
            response = self.session.get(html_url, timeout=10)
            
            if response.status_code != 200:
                return {"source": "error", "message": f"HTTP {response.status_code}"}
            
            soup = BeautifulSoup(response.text, "lxml")
            
            # Extract information from HTML
            name = repo
            
            # Description
            desc_elem = soup.find("p", class_="f4")
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Stars (look for star count in social counts)
            stars_elem = soup.find("a", href=f"/{owner}/{repo}/stargazers")
            stars = None
            if stars_elem:
                stars_text = stars_elem.get_text(strip=True)
                stars = self._parse_count(stars_text)
            
            return {
                "source": "html",
                "name": name,
                "description": description,
                "stars": stars,
                "url": html_url
            }
            
        except requests.RequestException as e:
            return {"source": "error", "message": str(e)}
    
    def _parse_count(self, text):
        """Parse count strings like '1.2k' to integers."""
        text = text.strip().lower()
        if "k" in text:
            return int(float(text.replace("k", "")) * 1000)
        elif "m" in text:
            return int(float(text.replace("m", "")) * 1000000)
        else:
            try:
                return int(text.replace(",", ""))
            except ValueError:
                return None

# Usage example
scraper = HybridScraper()

# Get info for a popular repository
repos_to_check = [
    ("python", "cpython"),
    ("requests", "requests"),
]

for owner, repo in repos_to_check:
    print(f"\nFetching {owner}/{repo}...")
    info = scraper.get_github_repo_info(owner, repo)
    
    print(f"  Source: {info.get('source')}")
    print(f"  Name: {info.get('name')}")
    print(f"  Description: {(info.get('description') or '')[:50]}...")
    print(f"  Stars: {info.get('stars')}")
```

The code implements a class that first attempts API access, providing  
structured data without parsing. If the API fails (rate limits, errors),  
it falls back to HTML scraping. This hybrid approach maximizes  
reliability while respecting rate limits.  

Sample output:  

```
Fetching python/cpython...
  Source: api
  Name: cpython
  Description: The Python programming language...
  Stars: 65234

Fetching requests/requests...
  Source: api
  Name: requests
  Description: A simple, yet elegant, HTTP library...
  Stars: 52145
```

**Best practices**:  
- Always check for API availability before scraping  
- Implement graceful degradation  
- Cache API responses to reduce requests  
- Handle rate limiting appropriately  

---

### Cleaning and Storing Scraped Data

Raw scraped data often requires cleaning before storage. This example  
demonstrates data cleaning and exporting to CSV and SQLite database.  

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import re
import os

def clean_text(text):
    """Clean and normalize text data."""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text.strip())
    # Remove special characters (keep basic punctuation)
    text = re.sub(r"[^\w\s.,!?'-]", "", text)
    return text

def clean_price(price_text):
    """Extract numeric price from text."""
    if not price_text:
        return None
    # Remove currency symbols and extract number
    numbers = re.findall(r"[\d,.]+", price_text)
    if numbers:
        try:
            return float(numbers[0].replace(",", ""))
        except ValueError:
            return None
    return None

def scrape_and_clean():
    """Scrape data, clean it, and return as DataFrame."""
    
    # Using JSONPlaceholder for sample data
    url = "https://jsonplaceholder.typicode.com/users"
    
    response = requests.get(url, timeout=10)
    
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return None
    
    users = response.json()
    
    # Clean and structure the data
    cleaned_data = []
    for user in users:
        cleaned_record = {
            "id": user.get("id"),
            "name": clean_text(user.get("name")),
            "username": clean_text(user.get("username")),
            "email": user.get("email", "").lower().strip(),
            "city": clean_text(user.get("address", {}).get("city")),
            "company": clean_text(user.get("company", {}).get("name")),
            "website": user.get("website", "").strip(),
        }
        
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", cleaned_record["email"]):
            cleaned_record["email"] = None
        
        cleaned_data.append(cleaned_record)
    
    return pd.DataFrame(cleaned_data)

def save_to_csv(df, filename):
    """Save DataFrame to CSV file."""
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Saved {len(df)} records to {filename}")

def save_to_sqlite(df, db_path, table_name):
    """Save DataFrame to SQLite database."""
    conn = sqlite3.connect(db_path)
    
    # Create table and insert data
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    
    # Verify insertion
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    
    conn.close()
    print(f"Saved {count} records to {db_path} (table: {table_name})")

# Execute the scraping and cleaning pipeline
print("Scraping and cleaning data...")
df = scrape_and_clean()

if df is not None:
    # Display cleaned data
    print("\nCleaned Data Preview:")
    print(df.to_string(max_rows=5))
    
    # Show data types and info
    print("\nData Types:")
    print(df.dtypes)
    
    # Save to different formats
    output_dir = "/tmp/scraped_data"
    os.makedirs(output_dir, exist_ok=True)
    
    csv_path = os.path.join(output_dir, "users.csv")
    save_to_csv(df, csv_path)
    
    db_path = os.path.join(output_dir, "scraped.db")
    save_to_sqlite(df, db_path, "users")
    
    # Query the SQLite database
    print("\nSample SQL Query:")
    conn = sqlite3.connect(db_path)
    query_result = pd.read_sql_query(
        "SELECT name, city, company FROM users LIMIT 3",
        conn
    )
    conn.close()
    print(query_result)
```

The code defines cleaning functions for text and numeric data. It uses  
regular expressions to normalize whitespace, remove special characters,  
and validate email formats. The pandas library enables easy data  
manipulation and export to CSV. SQLite provides persistent storage  
with SQL query capabilities.  

Sample output:  

```
Scraping and cleaning data...

Cleaned Data Preview:
   id           name    username              email       city          company
0   1  Leanne Graham       Bret  sincere@april.biz  Gwenborough    Romaguera-Crona
1   2   Ervin Howell  Antonette   shanna@melissa.tv     Wisokyburgh      Deckow-Crist
2   3  Clementine Bauch  Samantha  nathan@yesenia.net     McKenziehaven   Romaguera-Jacobson

Data Types:
id           int64
name        object
username    object
email       object
city        object
company     object
website     object
dtype: object

Saved 10 records to /tmp/scraped_data/users.csv
Saved 10 records to /tmp/scraped_data/scraped.db (table: users)

Sample SQL Query:
             name           city            company
0   Leanne Graham    Gwenborough    Romaguera-Crona
1    Ervin Howell    Wisokyburgh       Deckow-Crist
2  Clementine Bauch  McKenziehaven  Romaguera-Jacobson
```

**Data cleaning best practices**:  
- Normalize text by removing extra whitespace  
- Validate and standardize formats (emails, phones, dates)  
- Handle missing values consistently  
- Use appropriate data types for storage  
- Document cleaning transformations for reproducibility  

---

## Advanced Tips

### Request Headers and Browser Mimicking

Websites may block requests that don't appear to come from browsers.  
Use complete header sets:  

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
```

### Proxy Rotation

Rotate IP addresses to avoid blocking:  

```python
proxies = {
    "http": "http://proxy1.example.com:8080",
    "https": "http://proxy1.example.com:8080",
}
response = requests.get(url, proxies=proxies)
```

### Retry Logic with Exponential Backoff

Handle transient failures gracefully:  

```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
session.mount("https://", HTTPAdapter(max_retries=retries))
```

### Caching Responses

Avoid redundant requests by caching:  

```python
import requests_cache

# Cache responses for 1 hour
requests_cache.install_cache("scraper_cache", expire_after=3600)
```

---

## Common Pitfalls

- **Ignoring robots.txt**: Always check and respect crawl restrictions  
- **No rate limiting**: Sending requests too fast leads to IP blocks  
- **Hardcoded selectors**: Websites change; use flexible selectors  
- **Missing error handling**: Network issues and malformed HTML happen  
- **Not handling encoding**: Specify encoding or let libraries detect it  
- **Scraping dynamic content without JavaScript support**: Use Selenium  
- **Storing raw HTML**: Clean and structure data before storage  
- **No logging**: Add logging for debugging and monitoring  
- **Ignoring legal aspects**: Check Terms of Service and applicable laws  

---

## Resources for Further Learning

### Official Documentation

- [Requests Documentation](https://requests.readthedocs.io/)  
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)  
- [Scrapy Documentation](https://docs.scrapy.org/)  
- [Selenium with Python](https://selenium-python.readthedocs.io/)  
- [aiohttp Documentation](https://docs.aiohttp.org/)  

### Practice Websites

- [Quotes to Scrape](https://quotes.toscrape.com/) - Practice site for  
  learning web scraping  
- [Books to Scrape](https://books.toscrape.com/) - E-commerce practice site  
- [HTTPBin](https://httpbin.org/) - HTTP request/response testing  
- [JSONPlaceholder](https://jsonplaceholder.typicode.com/) - Fake API for  
  testing  

### Books and Courses

- "Web Scraping with Python" by Ryan Mitchell  
- "Python Web Scraping Cookbook" by Michael Heydt  
- Real Python Web Scraping tutorials  

### Tools and Services

- [Postman](https://www.postman.com/) - API testing and development  
- [Browser Developer Tools](https://developer.chrome.com/docs/devtools/) -  
  Inspect page structure  
- [Playwright](https://playwright.dev/) - Modern browser automation  

---

## Conclusion

Web scraping is a valuable skill for data collection and automation.  
By following ethical guidelines, implementing robust error handling,  
and using appropriate tools, you can build reliable scrapers for  
various applications. Always prefer official APIs when available,  
respect website policies, and handle data responsibly.  

Start with simple projects using Requests and BeautifulSoup, then  
progress to Selenium for dynamic content and Scrapy for large-scale  
crawling. Practice on designated training sites before scraping  
production websites.  
