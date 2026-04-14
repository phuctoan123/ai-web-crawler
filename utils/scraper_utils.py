import json
import os
from typing import List, Set, Tuple

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMExtractionStrategy,
)

from models.venue import Venue
from utils.data_utils import is_complete_venue, is_duplicate_venue


def _log(level: str, message: str) -> None:
    print(f"[{level}] {message}")


def _is_fatal_provider_error(message: str) -> bool:
    lower_msg = message.lower()
    fatal_patterns = [
        "insufficient balance",
        "invalid api key",
        "authentication",
        "unauthorized",
        "invalid_request_error",
        "not_found",
        "not found",
        "quota",
    ]
    return any(pattern in lower_msg for pattern in fatal_patterns)


def get_browser_config() -> BrowserConfig:
    """
    Returns the browser configuration for the crawler.

    Returns:
        BrowserConfig: The configuration settings for the browser.
    """
    # https://docs.crawl4ai.com/core/browser-crawler-config/
    return BrowserConfig(
        browser_type="chromium",  # Type of browser to simulate
        headless=False,  # Whether to run in headless mode (no GUI)
        verbose=True,  # Enable verbose logging
    )


def get_llm_strategy() -> LLMExtractionStrategy:
    """
    Returns the configuration for the language model extraction strategy.

    Returns:
        LLMExtractionStrategy: The settings for how to extract data using LLM.
    """
    # https://docs.crawl4ai.com/api/strategies/#llmextractionstrategy
    provider = os.getenv("LLM_PROVIDER", "gemini/gemini-2.0-flash")
    api_key = (
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or
        os.getenv("OPENAI_API_KEY")
        or os.getenv("LLM_API_KEY")
        or os.getenv("OLLAMA_API_KEY")
        or os.getenv("DEEPSEEK_API_KEY")
    )
    api_base = os.getenv("LLM_API_BASE") or os.getenv("OLLAMA_API_BASE")

    return LLMExtractionStrategy(
        provider=provider,
        api_token=api_key,
        api_base=api_base,
        schema=Venue.model_json_schema(),  # JSON schema of the data model
        extraction_type="schema",  # Type of extraction to perform
        instruction=(
            "Extract all VnExpress article objects with 'title', 'url', 'summary', "
            "'category', and 'published_at' (ISO datetime if available, otherwise empty string) "
            "from the following content."
        ),  # Instructions for the LLM
        input_format="markdown",  # Format of the input content
        verbose=True,  # Enable verbose logging
    )


async def fetch_and_process_page(
    crawler: AsyncWebCrawler,
    page_number: int,
    base_url: str,
    css_selector: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    required_keys: List[str],
    seen_names: Set[str],
) -> Tuple[List[dict], bool]:
    """
    Fetches and processes a single page of venue data.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        page_number (int): The page number to fetch.
        base_url (str): The base URL of the website.
        css_selector (str): The CSS selector to target the content.
        llm_strategy (LLMExtractionStrategy): The LLM extraction strategy.
        session_id (str): The session identifier.
        required_keys (List[str]): List of required keys in the venue data.
        seen_names (Set[str]): Set of venue names that have already been seen.

    Returns:
        Tuple[List[dict], bool]:
            - List[dict]: A list of processed venues from the page.
            - bool: A flag indicating if the "No Results Found" message was encountered.
    """
    url = f"{base_url}?page={page_number}"
    _log("INFO", f"Loading page {page_number}...")

    # Fetch page content with the extraction strategy
    try:
        result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,  # Do not use cached data
                extraction_strategy=llm_strategy,  # Strategy for data extraction
                css_selector=css_selector,  # Target specific content on the page
                session_id=session_id,  # Unique session ID for the crawl
            ),
        )
    except Exception as exc:
        _log("ERROR", f"Unhandled crawl exception on page {page_number}: {exc}")
        return [], True

    if not (result.success and result.extracted_content):
        _log("ERROR", f"Error fetching page {page_number}: {result.error_message}")
        return [], False

    # Parse extracted content
    try:
        extracted_data = json.loads(result.extracted_content)
    except json.JSONDecodeError as exc:
        _log(
            "ERROR",
            f"Invalid JSON extracted on page {page_number}: {exc}. Raw output will be skipped.",
        )
        return [], False

    if not extracted_data:
        _log("WARN", f"No extracted records found on page {page_number}.")
        return [], False

    # Process venues
    complete_venues = []
    for venue in extracted_data:
        if venue.get("error") is True:
            provider_error = str(venue.get("content", "Unknown extraction error"))
            _log("ERROR", f"Provider extraction error on page {page_number}: {provider_error}")
            if _is_fatal_provider_error(provider_error):
                _log("ERROR", "Fatal provider error detected. Stopping crawl gracefully.")
                return [], True
            continue

        # Ignore the 'error' key if it's False
        if venue.get("error") is False:
            venue.pop("error", None)  # Remove the 'error' key if it's False

        if not is_complete_venue(venue, required_keys):
            _log("WARN", f"Incomplete record skipped on page {page_number}: {venue}")
            continue  # Skip incomplete venues

        if is_duplicate_venue(venue["title"], seen_names):
            _log("INFO", f"Duplicate article '{venue['title']}' found. Skipping.")
            continue  # Skip duplicate venues

        # Add venue to the list
        seen_names.add(venue["title"])
        complete_venues.append(venue)

    if not complete_venues:
        _log("WARN", f"No complete records found on page {page_number}.")
        return [], False

    _log("INFO", f"Extracted {len(complete_venues)} records from page {page_number}.")
    return complete_venues, False  # Continue crawling
