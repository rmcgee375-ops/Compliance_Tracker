#!/usr/bin/env python3
"""
Compliance Updates Scraper - Working Version
Monitors NIST and GDPR websites for compliance updates.
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
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SCRAPER_VERSION = "1.2.0"


class ComplianceScraper:
    """Base class for scraping compliance websites."""
    
    def __init__(self, url: str, name: str, output_file: str):
        self.url = url
        self.name = name
        self.output_file = output_file
        self.timeout = int(os.getenv('SCRAPE_TIMEOUT', '15'))
        
    def fetch_page(self) -> Optional[BeautifulSoup]:
        """Fetch and parse the webpage."""
        try:
            logger.info(f"Fetching {self.name} from {self.url}")
            response = requests.get(
                self.url, 
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            response.raise_for_status()
            logger.info(f"Successfully fetched {self.name} (Status: {response.status_code})")
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
            return {"success": False, "new_count": 0, "total_count": 0, "error": "Failed to fetch page"}
        
        # Parse new updates
        new_updates = self.parse_updates(soup)
        if not new_updates:
            logger.warning(f"No updates found for {self.name}")
            return {"success": False, "new_count": 0, "total_count": 0, "error": "No updates parsed"}
        
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
                logger.info(f"New update found: {update['title'][:60]}...")
            
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
    """Scraper for NIST updates - uses text parsing approach."""
    
    def parse_updates(self, soup: BeautifulSoup) -> List[Dict]:
        updates = []
        
        # Find all links that look like news items
        # NIST structure: links with pattern /News/YYYY/...
        all_links = soup.find_all('a', href=True)
        logger.info(f"NIST: Found {len(all_links)} total links")
        
        seen_links = set()
        
        for link in all_links:
            href = link.get('href', '')
            
            # Look for NIST news pattern: /News/YYYY/...
            if re.match(r'/News/\d{4}/', href):
                # Get the link text (title)
                title = link.get_text(strip=True)
                
                # Skip if title is too short (navigation links)
                if not title or len(title) < 15:
                    continue
                
                full_link = urljoin(self.url, href)
                
                # Avoid duplicates
                if full_link in seen_links:
                    continue
                seen_links.add(full_link)
                
                # Try to find the date - look at next siblings or parent
                date_str = None
                parent = link.find_parent()
                if parent:
                    # Look for date pattern: "Month Day, Year"
                    text = parent.get_text()
                    date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}', text)
                    if date_match:
                        date_str = date_match.group(0)
                
                updates.append({
                    "title": title,
                    "link": full_link,
                    "published_date": date_str,
                    "scraped_date": datetime.now().strftime("%Y-%m-%d")
                })
                
                # Limit to first 15 updates
                if len(updates) >= 15:
                    break
        
        logger.info(f"NIST: Parsed {len(updates)} updates")
        return updates


class GDPRScraper(ComplianceScraper):
    """Scraper for GDPR/EU data protection updates."""
    
    def parse_updates(self, soup: BeautifulSoup) -> List[Dict]:
        updates = []
        
        # EDPB typically uses views-row or similar structures
        # Try multiple selectors
        items = soup.select('.views-row')
        
        if not items:
            # Fallback: look for news links
            all_links = soup.find_all('a', href=True)
            logger.info(f"GDPR: Trying fallback with {len(all_links)} links")
            
            seen_links = set()
            for link in all_links:
                href = link.get('href', '')
                
                # Look for news/press patterns
                if '/news/' in href or '/press/' in href.lower():
                    title = link.get_text(strip=True)
                    
                    if not title or len(title) < 15:
                        continue
                    
                    full_link = urljoin(self.url, href)
                    
                    if full_link in seen_links:
                        continue
                    seen_links.add(full_link)
                    
                    updates.append({
                        "title": title,
                        "link": full_link,
                        "published_date": None,
                        "scraped_date": datetime.now().strftime("%Y-%m-%d")
                    })
                    
                    if len(updates) >= 15:
                        break
        else:
            logger.info(f"GDPR: Found {len(items)} items with .views-row selector")
            
            for item in items[:15]:
                try:
                    # Find title and link
                    title_elem = item.find(['h3', 'h2', 'h4'])
                    link_elem = item.find('a', href=True)
                    
                    if not link_elem:
                        continue
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                    else:
                        title = link_elem.get_text(strip=True)
                    
                    if not title or len(title) < 10:
                        continue
                    
                    link = urljoin(self.url, link_elem.get('href', ''))
                    
                    # Try to find date
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
        
        logger.info(f"GDPR: Parsed {len(updates)} updates")
        return updates


def main():
    """Main execution function."""
    logger.info("Starting compliance scraper v" + SCRAPER_VERSION)
    
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
    logger.info("Summary:")
    for result in results:
        logger.info(f"  {result['source']}: {result['total_count']} total, {result['new_count']} new")
    
    # Output for GitHub Actions
    if os.getenv('GITHUB_ACTIONS'):
        with open(os.getenv('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
            f.write(f"new_updates={total_new}\n")
            f.write(f"has_updates={'true' if total_new > 0 else 'false'}\n")
    
    # Success if we got any updates
    return 0


if __name__ == "__main__":
    exit(main())
