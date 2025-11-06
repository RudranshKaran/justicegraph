"""
Cause List Ingestion Module for JusticeGraph.

Scrapes daily cause lists from Indian court websites and saves them
to the bronze layer for further processing.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.http_utils import fetch_url, download_file, get_page_with_post
from utils.io_utils import save_text, save_with_metadata, get_data_path, generate_filename
from utils.logging_utils import get_logger, log_scraper_activity

logger = get_logger('ingest')


class CauseListScraper:
    """
    Scraper for court cause lists (daily hearing schedules).
    
    Fetches cause lists from various court websites and saves them
    to the bronze layer for subsequent parsing.
    """
    
    def __init__(self, court_code: str, base_url: str):
        """
        Initialize the cause list scraper.
        
        Args:
            court_code: Standardized court code (e.g., 'DL-HC' for Delhi High Court)
            base_url: Base URL of the court's cause list portal
        
        Example:
            >>> scraper = CauseListScraper('DL-HC', 'https://delhihighcourt.nic.in')
            >>> scraper.fetch_cause_list(date(2023, 11, 15))
        """
        self.court_code = court_code
        self.base_url = base_url
        self.bronze_dir = get_data_path('bronze')
        
        logger.info(f"Initialized CauseListScraper for {court_code}")
    
    def fetch_cause_list(
        self,
        list_date: date,
        court_room: Optional[str] = None,
        judge_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Fetch cause list for a specific date and optional court/judge.
        
        Args:
            list_date: Date for which to fetch the cause list
            court_room: Optional court room number
            judge_name: Optional judge name
        
        Returns:
            Path to the saved file, or None if fetch failed
        
        Example:
            >>> scraper = CauseListScraper('DL-HC', 'https://delhihighcourt.nic.in')
            >>> file_path = scraper.fetch_cause_list(date(2023, 11, 15))
        """
        try:
            # Build URL or form data based on court portal structure
            # This is a template - actual implementation depends on specific court website
            url = f"{self.base_url}/causelists"
            
            # Example: POST-based search (common in Indian judicial websites)
            form_data = {
                'date': list_date.strftime('%d-%m-%Y'),
                'court_code': self.court_code
            }
            
            if court_room:
                form_data['court_room'] = court_room
            if judge_name:
                form_data['judge'] = judge_name
            
            logger.info(f"Fetching cause list for {self.court_code} on {list_date}")
            
            # Fetch the page
            response = get_page_with_post(url, form_data, timeout=60)
            
            if not response:
                log_scraper_activity(
                    logger,
                    'cause_list_ingest',
                    url,
                    'failed',
                    errors=['Failed to fetch page']
                )
                return None
            
            # Generate filename
            date_str = list_date.strftime('%Y%m%d')
            additional_parts = [self.court_code, date_str]
            if court_room:
                additional_parts.append(f"room_{court_room}")
            
            filename = generate_filename(
                'cause_list',
                'html',
                include_timestamp=True,
                additional_parts=additional_parts
            )
            
            # Save to bronze layer
            file_path = self.bronze_dir / filename
            save_text(response.text, file_path)
            
            # Save metadata
            metadata = {
                'court_code': self.court_code,
                'list_date': list_date.isoformat(),
                'court_room': court_room,
                'judge_name': judge_name,
                'source_url': url,
                'fetch_timestamp': datetime.utcnow().isoformat(),
                'content_length': len(response.text)
            }
            
            metadata_file = file_path.with_suffix('.json')
            save_with_metadata(
                {'html_file': filename},
                metadata_file,
                url,
                metadata
            )
            
            log_scraper_activity(
                logger,
                'cause_list_ingest',
                url,
                'success',
                record_count=1,
                court_code=self.court_code,
                list_date=list_date.isoformat()
            )
            
            return str(file_path)
            
        except Exception as e:
            logger.exception(f"Error fetching cause list: {e}")
            log_scraper_activity(
                logger,
                'cause_list_ingest',
                self.base_url,
                'failed',
                errors=[str(e)]
            )
            return None
    
    def fetch_cause_lists_range(
        self,
        start_date: date,
        end_date: date,
        delay_seconds: float = 2.0
    ) -> list:
        """
        Fetch cause lists for a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range (inclusive)
            delay_seconds: Delay between requests to avoid rate limiting
        
        Returns:
            List of file paths for successfully fetched cause lists
        
        Example:
            >>> scraper = CauseListScraper('DL-HC', 'https://delhihighcourt.nic.in')
            >>> files = scraper.fetch_cause_lists_range(
            ...     date(2023, 11, 1),
            ...     date(2023, 11, 7)
            ... )
        """
        import time
        
        file_paths = []
        current_date = start_date
        
        while current_date <= end_date:
            logger.info(f"Fetching cause list for {current_date}")
            
            file_path = self.fetch_cause_list(current_date)
            if file_path:
                file_paths.append(file_path)
            
            current_date += timedelta(days=1)
            
            # Rate limiting
            if current_date <= end_date:
                time.sleep(delay_seconds)
        
        logger.info(f"Fetched {len(file_paths)} cause lists from {start_date} to {end_date}")
        return file_paths


def fetch_ecourts_cause_list(
    state_code: str,
    district_code: str,
    court_code: str,
    list_date: date
) -> Optional[str]:
    """
    Fetch cause list from eCourts portal (template function).
    
    This is a template function for the National Judicial Data Grid (NJDG)
    or eCourts portal. Actual implementation depends on API availability.
    
    Args:
        state_code: State code (e.g., 'DL' for Delhi)
        district_code: District code
        court_code: Court complex code
        list_date: Date for the cause list
    
    Returns:
        Path to saved file, or None if failed
    
    Example:
        >>> file_path = fetch_ecourts_cause_list('DL', '01', 'DHC', date(2023, 11, 15))
    """
    base_url = "https://services.ecourts.gov.in/ecourtindia_v6/"
    
    scraper = CauseListScraper(
        court_code=f"{state_code}-{court_code}",
        base_url=base_url
    )
    
    return scraper.fetch_cause_list(list_date)


def fetch_high_court_cause_list(
    court_code: str,
    court_url: str,
    list_date: date,
    **kwargs
) -> Optional[str]:
    """
    Generic function to fetch cause list from High Court websites.
    
    Args:
        court_code: High Court code (e.g., 'DL-HC', 'MH-HC')
        court_url: Base URL of the High Court website
        list_date: Date for the cause list
        **kwargs: Additional parameters specific to the court website
    
    Returns:
        Path to saved file, or None if failed
    
    Example:
        >>> file_path = fetch_high_court_cause_list(
        ...     'DL-HC',
        ...     'https://delhihighcourt.nic.in',
        ...     date(2023, 11, 15),
        ...     bench='Regular Bench'
        ... )
    """
    scraper = CauseListScraper(court_code, court_url)
    return scraper.fetch_cause_list(list_date, **kwargs)


if __name__ == "__main__":
    """
    Example usage of the cause list scraper.
    Run this script directly to test the scraper functionality.
    """
    # Example: Fetch Delhi High Court cause list
    scraper = CauseListScraper(
        court_code='DL-HC',
        base_url='https://delhihighcourt.nic.in'
    )
    
    # Fetch today's cause list
    today = date.today()
    file_path = scraper.fetch_cause_list(today)
    
    if file_path:
        print(f"Successfully fetched cause list: {file_path}")
    else:
        print("Failed to fetch cause list")
    
    # Example: Fetch cause lists for the past week
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    
    files = scraper.fetch_cause_lists_range(start_date, end_date, delay_seconds=3.0)
    print(f"Fetched {len(files)} cause lists for the past week")
