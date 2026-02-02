"""Content extraction from HTML.

Extracts title and main content from parsed HTML.
"""

from bs4 import BeautifulSoup


class ContentExtractor:
    """Extracts content from HTML."""

    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            str: Page title
        """
        # Try h1 tag first
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        # Try title tag
        title = soup.find("title")
        if title:
            return title.get_text(strip=True)

        # Try meta og:title
        meta_title = soup.find("meta", property="og:title")
        if meta_title:
            content = meta_title.get("content", "")
            return str(content) if content else ""

        # Default
        return "Untitled"

    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            str: Main content text
        """
        # Remove unwanted elements
        for element in soup(
            [
                "script",
                "style",
                "nav",
                "header",
                "footer",
                "aside",
                "iframe",
                "noscript",
            ]
        ):
            element.decompose()

        # Try to find main content area
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_="content")
            or soup.find("div", class_="main")
            or soup.body
        )

        if main_content:
            # Get all paragraphs
            paragraphs = main_content.find_all("p")
            text = "\n\n".join(
                p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
            )
            return text

        # Fallback: get all text
        return soup.get_text(separator="\n", strip=True)

    def extract_all(self, soup: BeautifulSoup) -> dict[str, str]:
        """Extract all content from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            dict with 'title' and 'text' keys
        """
        return {
            "title": self.extract_title(soup),
            "text": self.extract_main_content(soup),
        }
