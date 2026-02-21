# Compliance_Tracker
Flat data scraping for privacy reg updates
# Compliance Updates Scraper

Automated tool to monitor information security and privacy regulation websites for updates. Runs on GitHub Actions and creates issues when new updates are found.

## Features

- 🔄 **Automated scraping** - Runs daily via GitHub Actions
- 🆕 **Smart detection** - Only notifies on truly new updates (hash-based deduplication)
- 📊 **Multiple sources** - Currently monitors NIST and GDPR/EDPB
- 🔔 **GitHub Issues** - Automatically creates issues for new updates
- 📦 **Version tracking** - Maintains historical data in JSON format
- 🛡️ **Robust error handling** - Graceful failures with detailed logging

## Monitored Sources

Currently tracking:

1. **NIST** - https://csrc.nist.gov/news
2. **GDPR/EDPB** - https://edpb.europa.eu/news/news_en
3. **DOL and USDA/APHIS** https://www.federalregister.gov/agencies
    "labor-department",
    "animal-and-plant-health-inspection-service"

## Setup

### 1. Fork or Clone This Repository

```bash
git clone https://github.com/yourusername/compliance-scraper.git
cd compliance-scraper
```

### 2. Enable GitHub Actions

1. Go to your repository Settings → Actions → General
2. Under "Workflow permissions", select "Read and write permissions"
3. Check "Allow GitHub Actions to create and approve pull requests"
4. Click Save

### 3. (Optional) Customize Schedule

Edit `.github/workflows/scrape.yml` to change the scraping schedule:

```yaml
schedule:
  - cron: '0 9 * * *'  # Daily at 9 AM UTC
```

Cron syntax examples:
- `0 9 * * *` - Daily at 9 AM UTC
- `0 9 * * 1` - Every Monday at 9 AM UTC
- `0 */6 * * *` - Every 6 hours

### 4. Run Manually (Optional)

Go to Actions → Compliance Updates Scraper → Run workflow

## Local Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Scraper

```bash
python src/scraper.py
```

### Test with Custom Timeout

```bash
SCRAPE_TIMEOUT=30 python src/scraper.py
```

## Adding New Sources

To add a new compliance source:

1. Create a new scraper class in `src/scraper.py`:

```python
class YourSourceScraper(ComplianceScraper):
    """Scraper for Your Source."""
    
    def parse_updates(self, soup: BeautifulSoup) -> List[Dict]:
        updates = []
        
        # Add your parsing logic here
        items = soup.select('.your-selector')
        
        for item in items:
            title_elem = item.find('h3')
            link_elem = item.find('a')
            
            if title_elem and link_elem:
                updates.append({
                    "title": title_elem.get_text(strip=True),
                    "link": urljoin(self.url, link_elem.get('href', '')),
                    "published_date": None,  # Add if available
                    "scraped_date": datetime.now().strftime("%Y-%m-%d")
                })
        
        return updates
```

2. Add it to the scrapers list in `main()`:

```python
scrapers = [
    # ... existing scrapers ...
    YourSourceScraper(
        url="https://example.com/updates",
        name="Your Source",
        output_file="compliance/yoursource-updates.json"
    ),
]
```

## Output Files

### `compliance/[source]-updates.json`

Individual source data:

```json
{
  "metadata": {
    "source": "https://csrc.nist.gov/news",
    "source_name": "NIST",
    "last_checked": "2025-02-14T10:30:00",
    "scraper_version": "1.0.0",
    "total_updates": 10,
    "new_updates": 2
  },
  "updates": [
    {
      "title": "New Cybersecurity Framework Released",
      "link": "https://csrc.nist.gov/news/2025/...",
      "published_date": "2025-02-10",
      "scraped_date": "2025-02-14",
      "hash": "abc123..."
    }
  ]
}
```

### `compliance/summary.json`

Overall summary:

```json
{
  "run_date": "2025-02-14T10:30:00",
  "total_new_updates": 3,
  "sources": [
    {
      "source": "NIST",
      "success": true,
      "new_count": 2,
      "total_count": 10
    }
  ]
}
```

## Configuration

### Environment Variables

Set these in GitHub Actions secrets or locally:

- `SCRAPE_TIMEOUT` - Request timeout in seconds (default: 10)
- `NIST_URL` - Custom NIST URL (optional)
- `GDPR_URL` - Custom GDPR URL (optional)

### GitHub Repository Settings

**Settings → Secrets and variables → Actions → New repository secret**

Add any custom URLs or API keys here.

## Troubleshooting

### No updates detected

1. Check the Actions logs for errors
2. Verify the website structure hasn't changed
3. Test locally: `python src/scraper.py`
4. Check if selectors need updating

### Scraper fails

- Check network connectivity
- Verify website is accessible
- Review error logs in Actions tab
- Increase timeout: Set `SCRAPE_TIMEOUT=30`

### Permission errors

Ensure GitHub Actions has write permissions:
Settings → Actions → General → Workflow permissions → Read and write permissions

## Notifications

### GitHub Issues

New updates automatically create GitHub Issues with:
- Number of new updates per source
- Date of discovery
- Links to view full data

### Email Notifications

To receive email notifications:
1. Watch this repository (Watch → All Activity)
2. Go to your GitHub notification settings
3. Enable notifications for Issues

### Slack/Discord Integration

Add a webhook step to `.github/workflows/scrape.yml`:

```yaml
- name: Notify Slack
  if: steps.summary.outputs.new_count > 0
  run: |
    curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"🔔 ${{ steps.summary.outputs.new_count }} new compliance updates!"}' \
    ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your scraper or improvements
4. Test locally
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Open a GitHub Issue
- Check existing issues for solutions
- Review GitHub Actions logs for errors
