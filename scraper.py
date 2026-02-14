URL = "https://csrc.nist.gov/news"
FILE_NAME = "compliance/nist-updates.json"

def scrape():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Logic depends on the specific site structure
    updates = []
    for item in soup.select('.document-wrapper')[:10]: # Adjust selector to site
        updates.append({
            "title": item.find('h4').text.strip(),
            "link": item.find('a')['href'],
            "date_checked": datetime.now().strftime("%Y-%m-%d")
        })
    
    # Save to file
    os.makedirs('compliance', exist_ok=True)
    with open(FILE_NAME, 'w') as f:
        json.dump(updates, f, indent=4)

if __name__ == "__main__":
    scrape()
