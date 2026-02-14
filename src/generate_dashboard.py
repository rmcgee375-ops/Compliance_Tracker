#!/usr/bin/env python3
"""
Compliance Dashboard Generator
Creates an easy-to-read HTML report from JSON compliance data.
"""

import json
import os
from datetime import datetime


def load_json_file(filepath):
    """Load a JSON file safely."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return None
    return None


def generate_html_dashboard():
    """Generate HTML dashboard from compliance JSON files."""
    
    # Load all data files
    nist_data = load_json_file('compliance/nist-updates.json')
    gdpr_data = load_json_file('compliance/gdpr-updates.json')
    fr_data = load_json_file('compliance/federal-register-updates.json')
    summary_data = load_json_file('compliance/summary.json')
    
    # Start HTML
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compliance Updates Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f7fa;
            padding: 20px;
            line-height: 1.6;
            color: #2c3e50;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .last-updated {
            color: #7f8c8d;
            font-size: 14px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #3498db;
        }
        
        .stat-label {
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 5px;
        }
        
        .new-badge {
            background: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 8px;
        }
        
        .section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #ecf0f1;
        }
        
        h2 {
            color: #2c3e50;
            font-size: 22px;
        }
        
        .source-badge {
            background: #3498db;
            color: white;
            padding: 5px 12px;
            border-radius: 5px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .update-item {
            padding: 15px;
            border-left: 4px solid #3498db;
            background: #f8f9fa;
            margin-bottom: 15px;
            border-radius: 5px;
        }
        
        .update-item.new {
            border-left-color: #e74c3c;
            background: #fff5f5;
        }
        
        .update-title {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 16px;
        }
        
        .update-title a {
            color: #2c3e50;
            text-decoration: none;
        }
        
        .update-title a:hover {
            color: #3498db;
        }
        
        .update-meta {
            display: flex;
            gap: 15px;
            color: #7f8c8d;
            font-size: 13px;
            flex-wrap: wrap;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .update-abstract {
            margin-top: 10px;
            color: #555;
            font-size: 14px;
            line-height: 1.5;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #95a5a6;
        }
        
        .filter-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 8px 16px;
            border: 2px solid #3498db;
            background: white;
            color: #3498db;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .filter-btn:hover {
            background: #3498db;
            color: white;
        }
        
        .filter-btn.active {
            background: #3498db;
            color: white;
        }
        
        @media (max-width: 768px) {
            .stats {
                grid-template-columns: 1fr;
            }
            
            .update-meta {
                flex-direction: column;
                gap: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📋 Compliance Updates Dashboard</h1>
            <div class="last-updated">Last updated: """ + datetime.now().strftime("%B %d, %Y at %I:%M %p") + """</div>
        </header>
"""
    
    # Add statistics
    total_updates = 0
    total_new = 0
    
    if summary_data:
        total_new = summary_data.get('total_new_updates', 0)
    
    if nist_data:
        total_updates += len(nist_data.get('updates', []))
    if gdpr_data:
        total_updates += len(gdpr_data.get('updates', []))
    if fr_data:
        total_updates += len(fr_data.get('updates', []))
    
    html += f"""
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_updates}</div>
                <div class="stat-label">Total Updates Tracked</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_new}</div>
                <div class="stat-label">New This Week</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">4</div>
                <div class="stat-label">Sources Monitored</div>
            </div>
        </div>
        
        <div class="filter-buttons">
            <button class="filter-btn active" onclick="filterUpdates('all')">All Updates</button>
            <button class="filter-btn" onclick="filterUpdates('new')">New Only</button>
            <button class="filter-btn" onclick="filterUpdates('nist')">NIST</button>
            <button class="filter-btn" onclick="filterUpdates('gdpr')">GDPR</button>
            <button class="filter-btn" onclick="filterUpdates('federal')">Federal Register</button>
        </div>
"""
    
    # Add NIST updates
    if nist_data and nist_data.get('updates'):
        new_count = nist_data.get('metadata', {}).get('new_updates', 0)
        html += f"""
        <div class="section" data-source="nist">
            <div class="section-header">
                <h2>NIST Updates</h2>
                <span class="source-badge">NIST{' <span class="new-badge">' + str(new_count) + ' NEW</span>' if new_count > 0 else ''}</span>
            </div>
"""
        
        for idx, update in enumerate(nist_data['updates'][:15]):
            is_new = idx < new_count
            new_class = ' new' if is_new else ''
            new_badge = '<span class="new-badge">NEW</span>' if is_new else ''
            
            html += f"""
            <div class="update-item{new_class}" data-new="{str(is_new).lower()}">
                <div class="update-title">
                    <a href="{update.get('link', '#')}" target="_blank">{update.get('title', 'No title')}</a>
                    {new_badge}
                </div>
                <div class="update-meta">
                    <div class="meta-item">📅 {update.get('published_date', 'Date unknown')}</div>
                    <div class="meta-item">🔍 Scraped: {update.get('scraped_date', 'Unknown')}</div>
                </div>
            </div>
"""
        
        html += """
        </div>
"""
    
    # Add GDPR updates
    if gdpr_data and gdpr_data.get('updates'):
        new_count = gdpr_data.get('metadata', {}).get('new_updates', 0)
        html += f"""
        <div class="section" data-source="gdpr">
            <div class="section-header">
                <h2>GDPR/EDPB Updates</h2>
                <span class="source-badge">GDPR{' <span class="new-badge">' + str(new_count) + ' NEW</span>' if new_count > 0 else ''}</span>
            </div>
"""
        
        for idx, update in enumerate(gdpr_data['updates'][:15]):
            is_new = idx < new_count
            new_class = ' new' if is_new else ''
            new_badge = '<span class="new-badge">NEW</span>' if is_new else ''
            
            html += f"""
            <div class="update-item{new_class}" data-new="{str(is_new).lower()}">
                <div class="update-title">
                    <a href="{update.get('link', '#')}" target="_blank">{update.get('title', 'No title')}</a>
                    {new_badge}
                </div>
                <div class="update-meta">
                    <div class="meta-item">📅 {update.get('published_date', 'Date unknown')}</div>
                    <div class="meta-item">🔍 Scraped: {update.get('scraped_date', 'Unknown')}</div>
                </div>
            </div>
"""
        
        html += """
        </div>
"""
    
    # Add Federal Register updates
    if fr_data and fr_data.get('updates'):
        new_count = fr_data.get('metadata', {}).get('new_updates', 0)
        html += f"""
        <div class="section" data-source="federal">
            <div class="section-header">
                <h2>Federal Register</h2>
                <span class="source-badge">Federal Register{' <span class="new-badge">' + str(new_count) + ' NEW</span>' if new_count > 0 else ''}</span>
            </div>
"""
        
        for idx, update in enumerate(fr_data['updates'][:15]):
            is_new = idx < new_count
            new_class = ' new' if is_new else ''
            new_badge = '<span class="new-badge">NEW</span>' if is_new else ''
            
            # Get agencies
            agencies = update.get('agencies', [])
            agency_names = [a.get('name', 'Unknown') for a in agencies] if isinstance(agencies, list) else []
            
            html += f"""
            <div class="update-item{new_class}" data-new="{str(is_new).lower()}">
                <div class="update-title">
                    <a href="{update.get('html_url', '#')}" target="_blank">{update.get('title', 'No title')}</a>
                    {new_badge}
                </div>
                <div class="update-meta">
                    <div class="meta-item">📅 Published: {update.get('publication_date', 'Unknown')}</div>
                    <div class="meta-item">📋 Type: {update.get('type', 'Unknown')}</div>
                    {f'<div class="meta-item">🏛️ {", ".join(agency_names[:2])}</div>' if agency_names else ''}
                </div>
"""
            
            if update.get('abstract'):
                abstract = update['abstract'][:200] + '...' if len(update.get('abstract', '')) > 200 else update.get('abstract', '')
                html += f"""
                <div class="update-abstract">{abstract}</div>
"""
            
            html += """
            </div>
"""
        
        html += """
        </div>
"""
    
    # Close HTML
    html += """
    </div>
    
    <script>
        function filterUpdates(filter) {
            // Update button states
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Show/hide sections and items
            const sections = document.querySelectorAll('.section');
            const items = document.querySelectorAll('.update-item');
            
            if (filter === 'all') {
                sections.forEach(s => s.style.display = 'block');
                items.forEach(i => i.style.display = 'block');
            } else if (filter === 'new') {
                sections.forEach(s => s.style.display = 'block');
                items.forEach(i => {
                    i.style.display = i.getAttribute('data-new') === 'true' ? 'block' : 'none';
                });
            } else {
                sections.forEach(s => {
                    s.style.display = s.getAttribute('data-source') === filter ? 'block' : 'none';
                });
                items.forEach(i => i.style.display = 'block');
            }
        }
    </script>
</body>
</html>
"""
    
    # Save HTML file
    output_path = 'compliance/dashboard.html'
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"Dashboard generated: {output_path}")
    print(f"Total updates: {total_updates}")
    print(f"New updates: {total_new}")


if __name__ == "__main__":
    generate_html_dashboard()
