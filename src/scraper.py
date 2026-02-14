#!/usr/bin/env python3
"""
Compliance Updates Scraper
Monitors various compliance and security regulation websites for updates.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import logging
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Dict, Optional
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Version for tracking scraper changes
SCRAPER_VERSION = "1.0.0"


class ComplianceScraper:
    """Base class for scraping compliance websites."""
    
    def __init__(self, url: str, name: str, output_file: str):
        self.url = url
        self.name = name
        self.output_file = output_file
        self.timeout = int(os.getenv('SCRAPE_TIMEOUT', '10'))
        
    def fetch_page(self) -> Optional[BeautifulSoup]:
        """Fetch and parse the webpage."""
        try:
            logger.info(f"Fetching {self.name} from {self.url}")
            response = requests.get(
                self.url, 
                timeout=self.timeout,
                headers={'User-Agent': 'ComplianceBot/1.0 (Compliance Monitoring)'}
            )
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {self.name}: {e}")
            return None
    
    def parse_updates(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse updates from the page. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement parse_updates")
    
    def load_existing_data(self) -> Dict:
        """Load existing scraped data if it exists."""
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load existing data: {e}")
        return {"updates": [], "metadata": {}}
    
    def save_data(self, updates: List[Dict], new_count: int):
        """Save scraped data to file."""
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        data = {
            "metadata": {
                "source": self.url,
                "source_name": self.name,
                "last_checked": datetime.now().isoformat(),
                "scraper_version": SCRAPER_VERSION,
                "total_updates": len(updates),
                "new_updates": new_count
            },
            "updates": updates
        }
        
        with open(self.output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {len(updates)} updates ({new_count} new) to {self.output_file}")
    
    def generate_hash(self, update: Dict) -> str:
        """Generate a unique hash for an update based on title and link."""
        content = f"{update.get('title', '')}{update.get('link', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def scrape(self) -> Dict:
        """Main scraping method."""
        soup = self.fetch_page()
        if not soup:
            return {"success": False, "new_count": 0, "total_count": 0}
        
        # Parse new updates
        new_updates = self.parse_updates(soup)
        if not new_updates:
            logger.warning(f"No updates found for {self.name}")
            return {"success": False, "new_count": 0, "total_count": 0}
        
        # Load existing data
        existing_data = self.load_existing_data()
        existing_updates = existing_data.get("updates", [])
        
        # Create hash set of existing updates
        existing_hashes = {self.generate_hash(u) for u in existing_updates}
        
        # Identify truly new updates
        truly_new = []
        all_updates = []
        
        for update in new_updates:
            update_hash = self.generate_hash(update)
            update['hash'] = update_hash
            
            if update_hash not in existing_hashes:
                truly_new.append(update)
                logger.info(f"New update found: {update['title']}")
            
            all_updates.append(update)
        
        # Save all current updates
        self.save_data(all_updates, len(truly_new))
        
        return {
            "success": True,
            "new_count": len(truly_new),
            "total_count": len(all_updates),
            "new_updates": truly_new
        }


class NISTScraper(ComplianceScraper):
    """Scraper for NIST updates."""
    
    def parse_updates(self, soup: BeautifulSoup) -> List[Dict]:
        updates = []
        
        # Try multiple possible selectors for NIST
        selectors = ['.document-wrapper', '.news-item', 'article', '.item']
        items = []
        
        for selector in selectors:
            items = soup.select(selector)[:10]
            if items:
                logger.info(f"Found items using selector: {selector}")
                break
        
        if not items:
            logger.warning("No items found with any selector")
            return updates
        
        for item in items:
            try:
                # Try multiple heading tags
                title_elem = item.find(['h4', 'h3', 'h2', 'a'])
                link_elem = item.find('a')
                
                if not title_elem or not link_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link = link_elem.get('href', '')
                
                if not title or not link:
                    continue
                
                # Handle relative URLs
                full_link = urljoin(self.url, link)
                
                # Try to find date
                date_elem = item.find(['time', 'span'], class_=['date', 'published'])
                date_str = date_elem.get_text(strip=True) if date_elem else None
                
                updates.append({
                    "title": title,
                    "link": full_link,
                    "published_date": date_str,
                    "scraped_date": datetime.now().strftime("%Y-%m-%d")
                })
            except Exception as e:
                logger.warning(f"Error parsing item: {e}")
                continue
        
        return updates


class GDPRScraper(ComplianceScraper):
    """Scraper for GDPR/EU data protection updates."""
    
    def parse_updates(self, soup: BeautifulSoup) -> List[Dict]:
        updates = []
        
        # Look for news items
        items = soup.select('.news-list-item, .press-item, article')[:10]
        
        for item in items:
            try:
                title_elem = item.find(['h3', 'h2', 'a'])
                link_elem = item.find('a')
                
                if not title_elem or not link_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link = urljoin(self.url, link_elem.get('href', ''))
                
                date_elem = item.find('time')
                date_str = date_elem.get_text(strip=True) if date_elem else None
                
                updates.append({
                    "title": title,
                    "link": link,
                    "published_date": date_str,
                    "scraped_date": datetime.now().strftime("%Y-%m-%d")
                })
            except Exception as e:
                logger.warning(f"Error parsing GDPR item: {e}")
                continue
        
        return updates


def main():
    """Main execution function."""
    logger.info("Starting compliance scraper")
    
    # Define sources to scrape
    scrapers = [
        NISTScraper(
            url=os.getenv('NIST_URL', 'https://csrc.nist.gov/news'),
            name="NIST",
            output_file="compliance/nist-updates.json"
        ),
        GDPRScraper(
            url=os.getenv('GDPR_URL', 'https://edpb.europa.eu/news/news_en'),
            name="GDPR/EDPB",
            output_file="compliance/gdpr-updates.json"
        ),
        # Add more scrapers as needed
    ]
    
    # Run all scrapers
    results = []
    total_new = 0
    
    for scraper in scrapers:
        result = scraper.scrape()
        results.append({
            "source": scraper.name,
            **result
        })
        total_new += result.get("new_count", 0)
    
    # Generate summary
    summary = {
        "run_date": datetime.now().isoformat(),
        "total_new_updates": total_new,
        "sources": results
    }
    
    # Save summary
    os.makedirs('compliance', exist_ok=True)
    with open('compliance/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Scraping complete. Total new updates: {total_new}")
    
    # Output for GitHub Actions
    if os.getenv('GITHUB_ACTIONS'):
        with open(os.getenv('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
            f.write(f"new_updates={total_new}\n")
            f.write(f"has_updates={'true' if total_new > 0 else 'false'}\n")
    
    return 0 if all(r['success'] for r in results) else 1


if __name__ == "__main__":
    exit(main())
