"""
HTTP utilities for JusticeGraph data ingestion.

Provides reusable functions for making HTTP requests with retries,
rate limiting, and error handling for web scraping and API calls.
"""

import time
import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger(__name__)


def create_session_with_retries(
    retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: tuple = (500, 502, 503, 504)
) -> requests.Session:
    """
    Create a requests session with automatic retry configuration.
    
    Args:
        retries: Maximum number of retry attempts
        backoff_factor: Backoff factor for exponential delay between retries
        status_forcelist: HTTP status codes that should trigger a retry
    
    Returns:
        Configured requests.Session object with retry adapter
    
    Example:
        >>> session = create_session_with_retries(retries=5)
        >>> response = session.get("https://example.com")
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch_url(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
    retries: int = 3,
    verify_ssl: bool = True
) -> Optional[requests.Response]:
    """
    Fetch content from a URL with error handling and retries.
    
    Args:
        url: The URL to fetch
        method: HTTP method (GET, POST, etc.)
        headers: Optional HTTP headers dictionary
        params: Optional query parameters dictionary
        data: Optional request body data (for POST requests)
        timeout: Request timeout in seconds
        retries: Number of retry attempts
        verify_ssl: Whether to verify SSL certificates
    
    Returns:
        requests.Response object if successful, None otherwise
    
    Example:
        >>> response = fetch_url("https://ecourts.gov.in/causelists", timeout=60)
        >>> if response:
        ...     print(response.text)
    """
    session = create_session_with_retries(retries=retries)
    
    # Default headers with User-Agent to avoid blocking
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    if headers:
        default_headers.update(headers)
    
    try:
        logger.info(f"Fetching URL: {url} with method: {method}")
        
        response = session.request(
            method=method,
            url=url,
            headers=default_headers,
            params=params,
            data=data,
            timeout=timeout,
            verify=verify_ssl
        )
        
        response.raise_for_status()
        logger.info(f"Successfully fetched URL: {url} (Status: {response.status_code})")
        return response
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching {url}: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error fetching {url}: {e}")
        return None
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error fetching {url}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching {url}: {e}")
        return None
    finally:
        session.close()


def download_file(
    url: str,
    save_path: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 60,
    chunk_size: int = 8192
) -> bool:
    """
    Download a file from a URL and save it to disk.
    
    Args:
        url: The URL of the file to download
        save_path: Local path where the file should be saved
        headers: Optional HTTP headers dictionary
        timeout: Request timeout in seconds
        chunk_size: Size of chunks to download (in bytes)
    
    Returns:
        True if download was successful, False otherwise
    
    Example:
        >>> success = download_file(
        ...     "https://example.com/judgment.pdf",
        ...     "data/bronze/judgment_12345.pdf"
        ... )
    """
    try:
        logger.info(f"Downloading file from {url} to {save_path}")
        
        response = fetch_url(url, timeout=timeout, headers=headers)
        if not response:
            return False
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"Successfully downloaded file to {save_path}")
        return True
        
    except IOError as e:
        logger.error(f"IO error saving file to {save_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error downloading file: {e}")
        return False


def rate_limit_request(delay: float = 1.0):
    """
    Decorator to add rate limiting to functions making HTTP requests.
    
    Args:
        delay: Delay in seconds between requests
    
    Example:
        >>> @rate_limit_request(delay=2.0)
        ... def fetch_cause_list(url):
        ...     return fetch_url(url)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_page_with_post(
    url: str,
    form_data: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30
) -> Optional[requests.Response]:
    """
    Submit a POST form and get the resulting page.
    Useful for Indian judicial websites that use POST forms for searches.
    
    Args:
        url: The URL to submit the form to
        form_data: Dictionary of form field names and values
        headers: Optional HTTP headers
        timeout: Request timeout in seconds
    
    Returns:
        requests.Response object if successful, None otherwise
    
    Example:
        >>> form_data = {
        ...     'court_code': 'DL',
        ...     'case_type': 'CRL',
        ...     'case_number': '123',
        ...     'case_year': '2023'
        ... }
        >>> response = get_page_with_post("https://example.com/search", form_data)
    """
    return fetch_url(
        url=url,
        method="POST",
        data=form_data,
        headers=headers,
        timeout=timeout
    )
