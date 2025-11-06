"""
Cause List Parser for JusticeGraph.

Parses HTML cause lists into structured DataFrames with standardized fields.
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import pandas as pd
from bs4 import BeautifulSoup
import re

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.io_utils import load_text, load_json, save_json, get_data_path
from utils.logging_utils import get_logger

logger = get_logger('parse')


class CauseListParser:
    """
    Parser for court cause lists.
    
    Extracts structured data from HTML cause lists including case numbers,
    parties, hearing times, judges, and purposes.
    """
    
    def __init__(self):
        """Initialize the cause list parser."""
        self.silver_dir = get_data_path('silver')
        logger.info("Initialized CauseListParser")
    
    def parse_html(self, html_content: str, court_code: str, list_date: date) -> pd.DataFrame:
        """
        Parse HTML cause list into a DataFrame.
        
        Args:
            html_content: HTML content of the cause list
            court_code: Court code for the cause list
            list_date: Date of the cause list
        
        Returns:
            DataFrame with parsed cause list entries
        
        Example:
            >>> parser = CauseListParser()
            >>> df = parser.parse_html(html_content, 'DL-HC', date(2023, 11, 15))
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # This is a template parser - actual implementation depends on HTML structure
            # Indian court websites vary significantly in their HTML structure
            
            entries = []
            
            # Common patterns in Indian court cause lists:
            # 1. Table-based layout with rows for each case
            # 2. Serial number, case number, parties, advocate, purpose columns
            
            # Try to find the main table
            tables = soup.find_all('table')
            
            if not tables:
                logger.warning("No tables found in cause list HTML")
                return self._create_empty_dataframe()
            
            # Usually the largest table contains the cause list
            main_table = max(tables, key=lambda t: len(t.find_all('tr')))
            rows = main_table.find_all('tr')
            
            if len(rows) < 2:
                logger.warning("Table has insufficient rows")
                return self._create_empty_dataframe()
            
            # Parse each row (skip header)
            for i, row in enumerate(rows[1:], start=1):
                cells = row.find_all(['td', 'th'])
                
                if len(cells) < 3:
                    continue
                
                # Extract text from each cell
                cell_texts = [self._clean_text(cell.get_text()) for cell in cells]
                
                # Map cells to fields (adjust based on actual structure)
                entry = self._extract_entry_from_cells(cell_texts, court_code, list_date)
                
                if entry:
                    entries.append(entry)
            
            df = pd.DataFrame(entries)
            logger.info(f"Parsed {len(df)} entries from cause list")
            
            return df
            
        except Exception as e:
            logger.exception(f"Error parsing cause list HTML: {e}")
            return self._create_empty_dataframe()
    
    def _extract_entry_from_cells(
        self,
        cells: List[str],
        court_code: str,
        list_date: date
    ) -> Optional[Dict[str, Any]]:
        """
        Extract a single cause list entry from table cells.
        
        Common column orders:
        - S.No, Case Number, Parties, Advocate, Purpose
        - S.No, Case Number, Case Title, Petitioner Advocate, Respondent Advocate, Stage
        """
        try:
            if len(cells) < 3:
                return None
            
            # Attempt to identify case number (usually contains /, numbers, and letters)
            case_number = None
            case_number_idx = None
            
            for idx, cell in enumerate(cells):
                if self._looks_like_case_number(cell):
                    case_number = cell
                    case_number_idx = idx
                    break
            
            if not case_number:
                return None
            
            entry = {
                'court_code': court_code,
                'list_date': list_date.isoformat(),
                'case_number': case_number,
                'serial_number': cells[0] if cells[0].isdigit() else None,
                'case_title': None,
                'petitioner': None,
                'respondent': None,
                'petitioner_advocate': None,
                'respondent_advocate': None,
                'purpose': None,
                'hearing_time': None,
                'court_room': None,
                'remarks': None
            }
            
            # Try to extract parties (usually in format "Party1 vs Party2")
            for cell in cells:
                if ' vs ' in cell.lower() or ' v. ' in cell.lower() or ' v/s ' in cell.lower():
                    parties = self._extract_parties(cell)
                    entry['petitioner'] = parties['petitioner']
                    entry['respondent'] = parties['respondent']
                    entry['case_title'] = cell
                    break
            
            # Look for advocate names (may contain keywords like "Adv.", "Advocate")
            for cell in cells:
                if 'adv' in cell.lower() and len(cell) > 3:
                    if not entry['petitioner_advocate']:
                        entry['petitioner_advocate'] = cell
                    elif not entry['respondent_advocate']:
                        entry['respondent_advocate'] = cell
            
            # Look for time patterns (HH:MM format)
            for cell in cells:
                if re.search(r'\d{1,2}:\d{2}', cell):
                    entry['hearing_time'] = cell
                    break
            
            # Purpose might be in the last column
            if case_number_idx is not None and len(cells) > case_number_idx + 1:
                possible_purpose = cells[-1]
                if len(possible_purpose) > 5 and not self._looks_like_case_number(possible_purpose):
                    entry['purpose'] = possible_purpose
            
            return entry
            
        except Exception as e:
            logger.exception(f"Error extracting entry from cells: {e}")
            return None
    
    def _looks_like_case_number(self, text: str) -> bool:
        """Check if text looks like a case number."""
        # Indian case numbers typically contain:
        # - Letters (case type abbreviations)
        # - Numbers
        # - Slashes or periods
        # - Year (4 digits)
        
        if not text or len(text) < 5:
            return False
        
        patterns = [
            r'[A-Z]+[./\s]*\d+[./\s]*\d{4}',  # CRL.A/123/2023
            r'[A-Z\s]+NO[.\s]*\d+',  # CRIMINAL APPEAL NO. 123
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_parties(self, text: str) -> Dict[str, Optional[str]]:
        """Extract petitioner and respondent from case title."""
        # Split on common separators
        separators = [' vs ', ' v. ', ' v/s ', ' versus ']
        
        parties: Dict[str, Optional[str]] = {'petitioner': None, 'respondent': None}
        
        for sep in separators:
            parts = text.split(sep)
            if len(parts) >= 2:
                parties['petitioner'] = parts[0].strip()
                parties['respondent'] = parts[1].strip()
                break
        
        return parties
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and special characters."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable())
        
        return text
    
    def _create_empty_dataframe(self) -> pd.DataFrame:
        """Create an empty DataFrame with standard columns."""
        columns = [
            'court_code', 'list_date', 'case_number', 'serial_number',
            'case_title', 'petitioner', 'respondent',
            'petitioner_advocate', 'respondent_advocate',
            'purpose', 'hearing_time', 'court_room', 'remarks'
        ]
        return pd.DataFrame(columns=columns)
    
    def parse_file(self, file_path: str) -> pd.DataFrame:
        """
        Parse a cause list HTML file.
        
        Args:
            file_path: Path to the HTML file
        
        Returns:
            DataFrame with parsed data
        
        Example:
            >>> parser = CauseListParser()
            >>> df = parser.parse_file('data/bronze/cause_list_DL_HC_20231115.html')
        """
        try:
            # Load HTML content
            html_content = load_text(file_path)
            if not html_content:
                logger.error(f"Could not load file: {file_path}")
                return self._create_empty_dataframe()
            
            # Load metadata if available
            metadata_path = Path(file_path).with_suffix('.json')
            metadata = load_json(str(metadata_path))
            
            court_code = metadata.get('data', {}).get('court_code', 'UNKNOWN') if metadata else 'UNKNOWN'
            list_date_str = metadata.get('data', {}).get('list_date') if metadata else None
            list_date = datetime.fromisoformat(list_date_str).date() if list_date_str else date.today()
            
            # Parse HTML
            df = self.parse_html(html_content, court_code, list_date)
            
            return df
            
        except Exception as e:
            logger.exception(f"Error parsing file {file_path}: {e}")
            return self._create_empty_dataframe()
    
    def parse_and_save(self, input_file: str, output_file: Optional[str] = None) -> str:
        """
        Parse a cause list and save to silver layer.
        
        Args:
            input_file: Path to bronze layer HTML file
            output_file: Optional path for output file (defaults to silver layer)
        
        Returns:
            Path to the saved CSV file
        
        Example:
            >>> parser = CauseListParser()
            >>> output_path = parser.parse_and_save(
            ...     'data/bronze/cause_list_DL_HC_20231115.html'
            ... )
        """
        try:
            # Parse the file
            df = self.parse_file(input_file)
            
            if df.empty:
                logger.warning(f"No data parsed from {input_file}")
            
            # Generate output filename
            if not output_file:
                input_path = Path(input_file)
                output_filename = input_path.stem + '_parsed.csv'
                output_file = str(self.silver_dir / output_filename)
            
            # Save to CSV
            df.to_csv(output_file, index=False)
            logger.info(f"Saved parsed data to {output_file} ({len(df)} rows)")
            
            # Also save as JSON for easier processing
            json_file = str(Path(output_file).with_suffix('.json'))
            df.to_json(json_file, orient='records', indent=2, date_format='iso')
            
            return output_file
            
        except Exception as e:
            logger.exception(f"Error in parse_and_save: {e}")
            raise


def batch_parse_cause_lists(input_dir: str, output_dir: Optional[str] = None) -> List[str]:
    """
    Parse all cause list HTML files in a directory.
    
    Args:
        input_dir: Directory containing HTML files
        output_dir: Optional output directory (defaults to silver layer)
    
    Returns:
        List of output file paths
    
    Example:
        >>> files = batch_parse_cause_lists('data/bronze')
    """
    from utils.io_utils import list_files_in_directory
    
    parser = CauseListParser()
    input_dir_path = Path(input_dir)
    
    # Find all HTML files
    html_files = list_files_in_directory(input_dir_path, pattern='cause_list_*.html')
    
    logger.info(f"Found {len(html_files)} cause list files to parse")
    
    output_files = []
    
    for html_file in html_files:
        try:
            output_file = parser.parse_and_save(str(html_file))
            output_files.append(output_file)
        except Exception as e:
            logger.error(f"Failed to parse {html_file}: {e}")
    
    logger.info(f"Successfully parsed {len(output_files)} cause lists")
    return output_files


if __name__ == "__main__":
    """Example usage of the cause list parser."""
    parser = CauseListParser()
    
    # Example: Parse a single file
    # Uncomment and modify path as needed
    # output_path = parser.parse_and_save('data/bronze/cause_list_sample.html')
    # print(f"Parsed file saved to: {output_path}")
    
    # Example: Batch parse all cause lists
    # output_files = batch_parse_cause_lists('data/bronze')
    # print(f"Parsed {len(output_files)} cause lists")
    
    print("CauseListParser module loaded successfully")
