# AI Competitor Tracker

## Project Overview
A web scraping application that monitors AI companies and generates daily competitive intelligence reports.

## Goal
Track competitors like OpenAI, Google AI, Microsoft AI, and others to understand:
- Product announcements
- Pricing changes  
- New features
- Market positioning

## Technical Stack
- Python for web scraping
- Beautiful Soup for HTML parsing
- Requests library for web requests
- JSON for data storage
- Markdown for report generation

## Key Features Needed
1. Web scraper that visits competitor websites
2. Data extraction from news/blog sections
3. Daily report generation in markdown format
4. Simple scheduling system

## File Structure
- `scraper.py` - Main scraping logic
- `config.json` - Website URLs and settings
- `reports/` - Generated daily reports
- `requirements.txt` - Python dependencies

## Development Approach
Start with a simple scraper for one website, then expand to multiple sources.