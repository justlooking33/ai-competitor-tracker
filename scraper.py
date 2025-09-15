#!/usr/bin/env python3
"""
AI Competitor Tracker - Web Scraper
Monitors AI companies and generates competitive intelligence reports.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import time

class CompetitorScraper:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_file} not found. Using default configuration.")
            return self.get_default_config()

    def get_default_config(self):
        return {
            "companies": {
                "OpenAI": {
                    "blog_url": "https://openai.com/blog/",
                    "selectors": {
                        "title": "h3",
                        "date": ".f-caption",
                        "link": "a"
                    }
                },
                "Google AI": {
                    "blog_url": "https://ai.googleblog.com/",
                    "selectors": {
                        "title": ".post-title",
                        "date": ".published",
                        "link": "a"
                    }
                }
            },
            "days_lookback": 7,
            "request_delay": 1
        }

    def scrape_company_news(self, company_name, company_config):
        print(f"Scraping {company_name}...")

        try:
            response = self.session.get(company_config['blog_url'], timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []

            # Use more flexible article finding approach
            if company_name == "Google AI":
                # Google Research blog specific structure
                article_elements = soup.find_all('a', href=lambda x: x and '/blog/' in x)[:10]
            else:
                # Generic approach for other sites
                article_elements = soup.find_all(['article', 'div'], class_=lambda x: x and any(
                    keyword in str(x).lower() for keyword in ['post', 'article', 'blog', 'news']
                ))[:10]  # Limit to 10 most recent

            for element in article_elements:
                article = self.extract_article_info(element, company_config['selectors'], company_name, company_config['blog_url'])
                if article and article['title'] != "No title":
                    articles.append(article)

            return articles

        except requests.RequestException as e:
            print(f"Error scraping {company_name}: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error scraping {company_name}: {e}")
            return []

    def extract_article_info(self, element, selectors, company_name, base_url):
        try:
            # Extract title based on selectors
            title_elem = None
            title_selectors = selectors['title'].split(', ')
            for selector in title_selectors:
                title_elem = element.select_one(selector.strip())
                if title_elem:
                    break

            if not title_elem and element.name == 'a':
                # For Google AI, the element itself might contain the title
                title_elem = element.select_one('h3') or element.select_one('h2')

            title = title_elem.get_text().strip() if title_elem else "No title"

            # Extract link
            if element.name == 'a':
                link = element.get('href', '')
            else:
                link_elem = element.find('a')
                link = link_elem.get('href', '') if link_elem else ''

            # Make relative links absolute
            if link and link.startswith('/'):
                from urllib.parse import urljoin
                link = urljoin(base_url, link)

            # Extract date
            date_elem = element.select_one(selectors.get('date', 'time'))
            if date_elem:
                date = date_elem.get_text().strip() or date_elem.get('datetime', 'Unknown date')
            else:
                date = "Unknown date"

            return {
                'title': title,
                'link': link,
                'date': date,
                'scraped_at': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error extracting article info: {e}")
            return None

    def scrape_all_companies(self):
        all_data = {}

        for company_name, company_config in self.config['companies'].items():
            articles = self.scrape_company_news(company_name, company_config)
            all_data[company_name] = articles

            # Be respectful with requests
            time.sleep(self.config.get('request_delay', 1))

        return all_data

    def generate_report(self, data):
        report_date = datetime.now().strftime('%Y-%m-%d')
        report_filename = f"reports/competitor_report_{report_date}.md"

        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)

        with open(report_filename, 'w') as f:
            f.write(f"# AI Competitor Intelligence Report\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for company_name, articles in data.items():
                f.write(f"## {company_name}\n\n")

                if not articles:
                    f.write("No recent articles found.\n\n")
                    continue

                for article in articles:
                    f.write(f"### {article['title']}\n")
                    f.write(f"**Date:** {article['date']}\n")
                    if article['link']:
                        f.write(f"**Link:** {article['link']}\n")
                    f.write("\n")

                f.write("\n")

        print(f"Report generated: {report_filename}")
        return report_filename

def main():
    scraper = CompetitorScraper()

    print("Starting AI Competitor Tracker...")
    print("=" * 50)

    # Scrape all companies
    data = scraper.scrape_all_companies()

    # Generate report
    report_file = scraper.generate_report(data)

    print("=" * 50)
    print(f"Scraping completed. Report saved to: {report_file}")

if __name__ == "__main__":
    main()