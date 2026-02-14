# Quick Start Guide

## 5-Minute Setup

### 1. Create Repository
```bash
# On GitHub: Create new repository named "compliance-scraper"
# Then clone it
git clone https://github.com/YOUR-USERNAME/compliance-scraper.git
cd compliance-scraper
```

### 2. Copy Files
Copy all files from this project into your new repository.

### 3. Enable GitHub Actions
1. Go to repository **Settings** → **Actions** → **General**
2. Under "Workflow permissions":
   - Select **"Read and write permissions"**
   - Check **"Allow GitHub Actions to create and approve pull requests"**
3. Click **Save**

### 4. Push and Run
```bash
git add .
git commit -m "Initial commit"
git push origin main

# Trigger first run
# Go to Actions tab → "Compliance Updates Scraper" → "Run workflow"
```

### 5. Watch for Updates
- Check **Actions** tab for run status
- New updates will create **Issues** automatically
- Data saved in **compliance/** folder

## What Happens Next?

- ✅ Scraper runs **daily at 9 AM UTC**
- ✅ Finds new compliance updates from NIST and GDPR sources  
- ✅ Creates GitHub Issue when updates found
- ✅ Commits data to repository
- ✅ You can run manually anytime

## Customize Schedule

Edit `.github/workflows/scrape.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # Change this line
```

**Examples:**
- `0 */6 * * *` - Every 6 hours
- `0 9 * * 1` - Every Monday at 9 AM
- `0 9 1 * *` - First day of month at 9 AM

## Add More Sources

Edit `src/scraper.py` and add to the `scrapers` list:

```python
scrapers = [
    NISTScraper(...),
    GDPRScraper(...),
    # Add your new scraper here
]
```

## Get Notifications

### Email
1. Click **Watch** (top right of repo)
2. Select **All Activity**
3. You'll get emails when Issues are created

### Slack/Teams
Add webhook URL to repository secrets, then add notification step to workflow.

## Need Help?

- Check **Actions** tab for error logs
- Review **README.md** for detailed docs
- Test locally: `python src/scraper.py`
