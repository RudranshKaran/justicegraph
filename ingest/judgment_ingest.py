"""
Judgment Ingestion Module for JusticeGraph.

Downloads judgment documents (PDF/HTML) from court repositories and saves
them to the bronze layer for text extraction and analysis.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import re

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.http_utils import fetch_url, download_file
from utils.io_utils import save_with_metadata, get_data_path, generate_filename, ensure_directory_exists
from utils.logging_utils import get_logger, log_scraper_activity

logger = get_logger('ingest')


class JudgmentScraper:
    """
    Scraper for downloading court judgments and orders.
    
    Fetches judgment documents in PDF or HTML format from various
    court repositories and judgment databases.
    """
    
    def __init__(self, court_code: str, base_url: str):
        """
        Initialize the judgment scraper.
        
        Args:
            court_code: Standardized court code
            base_url: Base URL of the judgment repository
        
        Example:
            >>> scraper = JudgmentScraper('DL-HC', 'https://delhihighcourt.nic.in')
        """
        self.court_code = court_code
        self.base_url = base_url
        self.bronze_dir = get_data_path('bronze')
        self.judgments_dir = self.bronze_dir / 'judgments'
        ensure_directory_exists(self.judgments_dir)
        
        logger.info(f"Initialized JudgmentScraper for {court_code}")
    
    def fetch_judgment(
        self,
        judgment_url: str,
        case_number: Optional[str] = None,
        judgment_date: Optional[date] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Download a judgment document from a URL.
        
        Args:
            judgment_url: URL of the judgment document
            case_number: Associated case number
            judgment_date: Date of the judgment
            metadata: Additional metadata about the judgment
        
        Returns:
            Dictionary with file path and metadata, or None if failed
        
        Example:
            >>> scraper = JudgmentScraper('DL-HC', 'https://delhihighcourt.nic.in')
            >>> result = scraper.fetch_judgment(
            ...     'https://example.com/judgments/123.pdf',
            ...     case_number='CRL.A/123/2023',
            ...     judgment_date=date(2023, 11, 15)
            ... )
        """
        try:
            logger.info(f"Fetching judgment from {judgment_url}")
            
            # Determine file extension from URL
            extension = 'pdf' if '.pdf' in judgment_url.lower() else 'html'
            
            # Generate filename
            additional_parts = [self.court_code]
            if case_number:
                safe_case_num = re.sub(r'[^\w\-]', '_', case_number)
                additional_parts.append(safe_case_num)
            if judgment_date:
                additional_parts.append(judgment_date.strftime('%Y%m%d'))
            
            filename = generate_filename(
                'judgment',
                extension,
                include_timestamp=True,
                additional_parts=additional_parts
            )
            
            file_path = self.judgments_dir / filename
            
            # Download the file
            if extension == 'pdf':
                success = download_file(judgment_url, str(file_path), timeout=120)
            else:
                response = fetch_url(judgment_url, timeout=60)
                if response:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    success = True
                else:
                    success = False
            
            if not success:
                log_scraper_activity(
                    logger,
                    'judgment_ingest',
                    judgment_url,
                    'failed',
                    errors=['Failed to download judgment']
                )
                return None
            
            # Prepare metadata
            judgment_metadata = {
                'court_code': self.court_code,
                'case_number': case_number,
                'judgment_date': judgment_date.isoformat() if judgment_date else None,
                'judgment_url': judgment_url,
                'file_type': extension,
                'filename': filename,
                'fetch_timestamp': datetime.utcnow().isoformat()
            }
            
            if metadata:
                judgment_metadata.update(metadata)
            
            # Save metadata
            metadata_file = file_path.with_suffix('.json')
            save_with_metadata(
                {'judgment_file': filename},
                metadata_file,
                judgment_url,
                judgment_metadata
            )
            
            log_scraper_activity(
                logger,
                'judgment_ingest',
                judgment_url,
                'success',
                record_count=1,
                case_number=case_number
            )
            
            return {
                'file_path': str(file_path),
                'metadata_path': str(metadata_file),
                'case_number': case_number,
                'metadata': judgment_metadata
            }
            
        except Exception as e:
            logger.exception(f"Error fetching judgment: {e}")
            log_scraper_activity(
                logger,
                'judgment_ingest',
                judgment_url,
                'failed',
                errors=[str(e)]
            )
            return None
    
    def fetch_judgments_by_date_range(
        self,
        start_date: date,
        end_date: date,
        delay_seconds: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Fetch judgments pronounced within a date range.
        
        This is a template method - actual implementation depends on the
        specific court's API or search interface.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            delay_seconds: Delay between requests
        
        Returns:
            List of judgment data dictionaries
        
        Example:
            >>> scraper = JudgmentScraper('DL-HC', 'https://delhihighcourt.nic.in')
            >>> judgments = scraper.fetch_judgments_by_date_range(
            ...     date(2023, 11, 1),
            ...     date(2023, 11, 7)
            ... )
        """
        import time
        
        # This is a template - actual implementation would:
        # 1. Query the court's judgment search API/page
        # 2. Get list of judgment URLs
        # 3. Download each judgment
        
        logger.info(f"Fetching judgments from {start_date} to {end_date}")
        
        # Example structure (to be customized per court)
        search_url = f"{self.base_url}/judgments/search"
        
        results = []
        
        # Placeholder for actual search and download logic
        # In practice, you would:
        # - Submit search form with date range
        # - Parse result page for judgment links
        # - Download each judgment using fetch_judgment()
        
        logger.info(f"Fetched {len(results)} judgments")
        return results
    
    def fetch_judgment_for_case(
        self,
        case_number: str,
        case_type: Optional[str] = None,
        case_year: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch the judgment for a specific case number.
        
        Args:
            case_number: Case number
            case_type: Case type
            case_year: Case year
        
        Returns:
            Dictionary with judgment data, or None if not found
        
        Example:
            >>> scraper = JudgmentScraper('DL-HC', 'https://delhihighcourt.nic.in')
            >>> judgment = scraper.fetch_judgment_for_case('CRL.A/123/2023')
        """
        try:
            # Template - actual implementation depends on court website
            search_url = f"{self.base_url}/judgments/case_search"
            
            logger.info(f"Searching for judgment for case {case_number}")
            
            # Would submit search form and extract judgment URL
            # Then download using fetch_judgment()
            
            # Placeholder
            return None
            
        except Exception as e:
            logger.exception(f"Error fetching judgment for case {case_number}: {e}")
            return None


def fetch_indiankanoon_judgment(
    search_query: str,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Search and fetch judgments from IndianKanoon.
    
    IndianKanoon is a public repository of Indian case law.
    This is a template function for educational purposes.
    
    Args:
        search_query: Search query (case name, keywords, etc.)
        max_results: Maximum number of results to fetch
    
    Returns:
        List of judgment data dictionaries
    
    Example:
        >>> judgments = fetch_indiankanoon_judgment('habeas corpus delhi', max_results=5)
    """
    base_url = "https://indiankanoon.org"
    
    scraper = JudgmentScraper('INDIAN-KANOON', base_url)
    
    # Template - would implement search and download logic
    logger.info(f"Searching IndianKanoon for: {search_query}")
    
    return []


def fetch_sci_judgment(
    case_number: str,
    year: str
) -> Optional[Dict[str, Any]]:
    """
    Fetch judgment from Supreme Court of India website.
    
    Template function for Supreme Court judgments.
    
    Args:
        case_number: SCI case number
        year: Case year
    
    Returns:
        Dictionary with judgment data, or None if failed
    
    Example:
        >>> judgment = fetch_sci_judgment('123', '2023')
    """
    base_url = "https://main.sci.gov.in"
    
    scraper = JudgmentScraper('SC-INDIA', base_url)
    
    # Template for SCI-specific logic
    full_case_number = f"SCI/{case_number}/{year}"
    
    logger.info(f"Fetching SCI judgment for {full_case_number}")
    
    return None


def batch_download_judgments(
    judgment_urls: List[str],
    court_code: str,
    delay_seconds: float = 3.0,
    metadata_list: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Batch download multiple judgments from a list of URLs.
    
    Args:
        judgment_urls: List of judgment URLs
        court_code: Court code
        delay_seconds: Delay between downloads
        metadata_list: Optional list of metadata dicts (one per URL)
    
    Returns:
        List of successfully downloaded judgment data
    
    Example:
        >>> urls = [
        ...     'https://example.com/judgment1.pdf',
        ...     'https://example.com/judgment2.pdf'
        ... ]
        >>> results = batch_download_judgments(urls, 'DL-HC', delay_seconds=5.0)
    """
    import time
    
    scraper = JudgmentScraper(court_code, "")
    results = []
    
    for i, url in enumerate(judgment_urls):
        metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else None
        
        logger.info(f"Downloading judgment {i+1}/{len(judgment_urls)}")
        
        result = scraper.fetch_judgment(url, metadata=metadata)
        if result:
            results.append(result)
        
        # Rate limiting
        if i < len(judgment_urls) - 1:
            time.sleep(delay_seconds)
    
    logger.info(f"Downloaded {len(results)}/{len(judgment_urls)} judgments")
    return results


if __name__ == "__main__":
    """
    Example usage of the judgment scraper.
    """
    # Example: Download a judgment from Delhi High Court
    scraper = JudgmentScraper(
        court_code='DL-HC',
        base_url='https://delhihighcourt.nic.in'
    )
    
    # Example judgment URL (placeholder)
    judgment_url = 'https://example.com/judgments/sample.pdf'
    
    result = scraper.fetch_judgment(
        judgment_url,
        case_number='CRL.A/123/2023',
        judgment_date=date(2023, 11, 15)
    )
    
    if result:
        print(f"Successfully downloaded judgment: {result['file_path']}")
    else:
        print("Failed to download judgment")
