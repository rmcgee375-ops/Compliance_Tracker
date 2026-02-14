#!/usr/bin/env python3
"""
Federal Register Compliance Scraper
Monitors specific agencies for new regulatory documents.
"""

import requests
import json
import os
import logging
from datetime import datetime, timedelta
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CONFIGURATION: Agencies to monitor
# Slugs from https://www.federalregister.gov/agencies
AGENCIES = [
    "labor-department",
    "animal-and-plant-health-inspection-service"
]

FILE_PATH = "compliance/federal-register-updates.json"


def generate_hash(update: dict) -> str:
    """Generate a unique hash for a document."""
    content = f"{update.get('title', '')}{update.get('html_url', '')}"
    return hashlib.md5(content.encode()).hexdigest()


def get_updates():
    """Fetch documents from Federal Register API."""
    # Calculate date from 7 days ago
    since_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    logger.info(f"Fetching Federal Register updates since {since_date}")
    
    # Federal Register API endpoint
    url = "https://www.federalregister.gov/api/v1/documents.json"
    params = {
        "fields[]": ["title", "type", "abstract", "html_url", "publication_date", "agencies"],
        "per_page": 50,
        "order": "newest",
        "conditions[publication_date][gte]": since_date,
        "conditions[agencies][]": AGENCIES
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        results = data.get('results', [])
        
        logger.info(f"Found {len(results)} documents from Federal Register")
        return results
        
    except requests.RequestException as e:
        logger.error(f"Error fetching Federal Register data: {e}")
        return []


def load_existing_data():
    """Load existing Federal Register data if it exists."""
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not load existing data: {e}")
    return {"updates": [], "metadata": {}}


def save_and_compare(new_updates):
    """Save updates and identify new ones."""
    os.makedirs('compliance', exist_ok=True)
    
    # Load existing data
    existing_data = load_existing_data()
    existing_updates = existing_data.get("updates", [])
    
    # Create hash set of existing updates
    existing_hashes = {generate_hash(u) for u in existing_updates}
    
    # Identify truly new updates
    truly_new = []
    all_updates = []
    
    for update in new_updates:
        update_hash = generate_hash(update)
        update['hash'] = update_hash
        
        if update_hash not in existing_hashes:
            truly_new.append(update)
            logger.info(f"New document: {update.get('title', 'Unknown')[:60]}...")
        
        all_updates.append(update)
    
    # Prepare data to save
    data = {
        "metadata": {
            "last_checked": datetime.now().isoformat(),
            "agencies": AGENCIES,
            "total_updates": len(all_updates),
            "new_updates": len(truly_new),
            "lookback_days": 7
        },
        "updates": all_updates
    }
    
    # Save to file
    with open(FILE_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved {len(all_updates)} documents ({len(truly_new)} new)")
    
    # Output for GitHub Actions
    if os.getenv('GITHUB_ACTIONS'):
        with open(os.getenv('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
            f.write(f"new_updates={len(truly_new)}\n")
            f.write(f"has_updates={'true' if len(truly_new) > 0 else 'false'}\n")
    
    return len(truly_new)


if __name__ == "__main__":
    logger.info("Starting Federal Register scraper")
    updates = get_updates()
    new_count = save_and_compare(updates)
    logger.info(f"Federal Register scraping complete. New documents: {new_count}")
