import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AngelOneScraper:
    def __init__(self, base_url="https://www.angelone.in/support"):
        self.base_url = base_url
        self.visited_urls = set()
        self.output_dir = "docs/angelone"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

    def get_page_content(self, url):
        """Fetch and parse a webpage."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def extract_text(self, soup):
        """Extract relevant text content from the page."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text

    def save_content(self, url, content):
        """Save the extracted content to a file."""
        # Create a filename from the URL
        filename = url.replace(self.base_url, "").replace("/", "_").strip("_")
        if not filename:
            filename = "home"
        filename = f"{filename}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Source URL: {url}\n\n")
            f.write(content)
        
        logger.info(f"Saved content from {url} to {filepath}")

    def scrape_page(self, url):
        """Scrape a single page and its linked pages."""
        if url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        logger.info(f"Scraping: {url}")
        
        # Get page content
        content = self.get_page_content(url)
        if not content:
            return
        
        # Parse the page
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract and save the main content
        text_content = self.extract_text(soup)
        self.save_content(url, text_content)
        
        # Find and follow links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            
            # Only follow links within the support section
            if full_url.startswith(self.base_url) and full_url not in self.visited_urls:
                time.sleep(1)  # Be nice to the server
                self.scrape_page(full_url)

    def start_scraping(self):
        """Start the scraping process from the base URL."""
        logger.info("Starting scraping process...")
        self.scrape_page(self.base_url)
        logger.info("Scraping completed!")

if __name__ == "__main__":
    scraper = AngelOneScraper()
    scraper.start_scraping() 