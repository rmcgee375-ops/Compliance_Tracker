"""
Basic tests for the compliance scraper.
Run with: pytest tests/test_scraper.py
"""

import pytest
import json
import os
from src.scraper import ComplianceScraper, NISTScraper, GDPRScraper
from unittest.mock import Mock, patch, mock_open


class TestComplianceScraper:
    """Test the base ComplianceScraper class."""
    
    def test_generate_hash(self):
        """Test that hashes are generated consistently."""
        scraper = NISTScraper(
            url="https://example.com",
            name="Test",
            output_file="test.json"
        )
        
        update1 = {"title": "Test Update", "link": "https://example.com/1"}
        update2 = {"title": "Test Update", "link": "https://example.com/1"}
        update3 = {"title": "Different", "link": "https://example.com/1"}
        
        hash1 = scraper.generate_hash(update1)
        hash2 = scraper.generate_hash(update2)
        hash3 = scraper.generate_hash(update3)
        
        assert hash1 == hash2, "Same updates should have same hash"
        assert hash1 != hash3, "Different updates should have different hash"
    
    def test_load_existing_data_no_file(self):
        """Test loading data when file doesn't exist."""
        scraper = NISTScraper(
            url="https://example.com",
            name="Test",
            output_file="/tmp/nonexistent.json"
        )
        
        data = scraper.load_existing_data()
        assert data == {"updates": [], "metadata": {}}
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"updates": [{"title": "Test"}], "metadata": {}}')
    def test_load_existing_data_success(self, mock_file):
        """Test loading existing data successfully."""
        scraper = NISTScraper(
            url="https://example.com",
            name="Test",
            output_file="test.json"
        )
        
        data = scraper.load_existing_data()
        assert "updates" in data
        assert len(data["updates"]) == 1


class TestNISTScraper:
    """Test the NIST scraper."""
    
    @patch('requests.get')
    def test_fetch_page_success(self, mock_get):
        """Test successful page fetch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><h1>Test</h1></body></html>"
        mock_get.return_value = mock_response
        
        scraper = NISTScraper(
            url="https://csrc.nist.gov/news",
            name="NIST",
            output_file="nist.json"
        )
        
        soup = scraper.fetch_page()
        assert soup is not None
        assert soup.find('h1').text == "Test"
    
    @patch('requests.get')
    def test_fetch_page_failure(self, mock_get):
        """Test handling of fetch failures."""
        mock_get.side_effect = Exception("Network error")
        
        scraper = NISTScraper(
            url="https://csrc.nist.gov/news",
            name="NIST",
            output_file="nist.json"
        )
        
        soup = scraper.fetch_page()
        assert soup is None
    
    def test_parse_updates_with_valid_html(self):
        """Test parsing with valid HTML structure."""
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <body>
                <div class="document-wrapper">
                    <h4>Security Update</h4>
                    <a href="/news/2025/update">Read more</a>
                </div>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        scraper = NISTScraper(
            url="https://csrc.nist.gov/news",
            name="NIST",
            output_file="nist.json"
        )
        
        updates = scraper.parse_updates(soup)
        assert len(updates) > 0
        assert "title" in updates[0]
        assert "link" in updates[0]


class TestIntegration:
    """Integration tests."""
    
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_full_scrape_flow(self, mock_file, mock_get):
        """Test the complete scraping flow."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <div class="document-wrapper">
                    <h4>Test Update</h4>
                    <a href="/update">Link</a>
                </div>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        scraper = NISTScraper(
            url="https://example.com",
            name="Test",
            output_file="/tmp/test.json"
        )
        
        result = scraper.scrape()
        
        assert result["success"] is True
        assert result["total_count"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
