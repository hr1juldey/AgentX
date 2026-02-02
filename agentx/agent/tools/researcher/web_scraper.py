"""Web Scraper Module for Researcher agent.

Ported from R014: services/tools/researcher/web_scraper.py

Provides web scraping capabilities for extracting main content
from URLs. Uses beautifulsoup4 for HTML parsing.

This is a facade for backward compatibility. Actual implementation has been
moved to the scraper/ subdirectory.
"""

from agentx.agent.tools.researcher.scraper import WebScraperModule

__all__ = ["WebScraperModule"]
