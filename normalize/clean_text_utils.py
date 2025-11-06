"""
Text cleaning utilities for JusticeGraph.

Provides generic text normalization functions for judicial data.
"""

import re
from typing import Optional
import unicodedata


def remove_extra_whitespace(text: str) -> str:
    """Remove extra whitespace, tabs, and newlines from text."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def remove_honorifics(text: str) -> str:
    """
    Remove common honorifics from names.
    
    Args:
        text: Input text with honorifics
    
    Returns:
        Text with honorifics removed
    
    Example:
        >>> remove_honorifics("Hon'ble Mr. Justice John Doe")
        'John Doe'
    """
    if not text:
        return ""
    
    honorifics = [
        r"Hon'ble\s+",
        r"Honourable\s+",
        r"Mr\.\s+",
        r"Ms\.\s+",
        r"Mrs\.\s+",
        r"Dr\.\s+",
        r"Justice\s+",
        r"Judge\s+",
        r"Chief\s+Justice\s+",
        r"Adv\.\s+",
        r"Advocate\s+",
        r"Sr\.\s+",
        r"Shri\s+",
        r"Smt\.\s+",
    ]
    
    result = text
    for pattern in honorifics:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    
    return remove_extra_whitespace(result)


def normalize_case_number(case_number: str) -> str:
    """
    Normalize case number to standard format: TYPE/NUMBER/YEAR.
    
    Args:
        case_number: Raw case number
    
    Returns:
        Normalized case number
    
    Example:
        >>> normalize_case_number("CRL. A.  123 of 2023")
        'CRL.A/123/2023'
    """
    if not case_number:
        return ""
    
    # Remove extra whitespace
    case_number = remove_extra_whitespace(case_number)
    
    # Try to extract components
    patterns = [
        # Match patterns like "CRL.A/123/2023" or "CRL. A. 123 of 2023"
        r'([A-Z][A-Z\.\s]+?)\s*(\d+)\s+(?:of|OF)\s+(\d{4})',
        # Match patterns like "CRL.A/123/2023" or "CRL.A 123/2023"
        r'([A-Z][A-Z\.]+)[/\s]+(\d+)[/\s]+(\d{4})',
        # Match patterns like "CIVIL APPEAL NO. 123/2023"
        r'([A-Z\s]+)\s+NO\.\s*(\d+)[/\s]+(\d{4})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, case_number, re.IGNORECASE)
        if match:
            case_type = match.group(1).strip().upper()
            # Remove spaces and ensure dots between abbreviations
            case_type = re.sub(r'\s+', '.', case_type)
            # Remove any trailing dots
            case_type = case_type.rstrip('.')
            # Ensure single dots between parts
            case_type = re.sub(r'\.+', '.', case_type)
            case_num = match.group(2)
            year = match.group(3)
            return f"{case_type}/{case_num}/{year}"
    
    # If no pattern matches, return cleaned version
    return case_number.upper()


def standardize_court_name(court_name: str) -> str:
    """
    Standardize court names.
    
    Args:
        court_name: Raw court name
    
    Returns:
        Standardized court name
    
    Example:
        >>> standardize_court_name("HIGH COURT OF DELHI")
        'Delhi High Court'
    """
    if not court_name:
        return ""
    
    court_name = remove_extra_whitespace(court_name)
    
    # Mapping of common variations
    replacements = {
        r'HIGH\s+COURT\s+OF\s+(\w+)': r'\1 High Court',
        r'(\w+)\s+HIGH\s+COURT': r'\1 High Court',
        r'SUPREME\s+COURT\s+OF\s+INDIA': 'Supreme Court of India',
        r'DISTRICT\s+COURT': 'District Court',
    }
    
    result = court_name.title()
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result


def clean_name(name: str) -> str:
    """
    Clean and normalize person names (judges, advocates, parties).
    
    Args:
        name: Raw name
    
    Returns:
        Cleaned name
    
    Example:
        >>> clean_name("  Hon'ble Mr. Justice JOHN DOE  ")
        'John Doe'
    """
    if not name:
        return ""
    
    # Remove honorifics
    name = remove_honorifics(name)
    
    # Remove extra punctuation
    name = re.sub(r'[^\w\s.-]', '', name)
    
    # Proper case
    name = name.title()
    
    # Remove extra whitespace
    name = remove_extra_whitespace(name)
    
    return name


def normalize_date_format(date_str: str) -> Optional[str]:
    """
    Normalize date strings to ISO format (YYYY-MM-DD).
    
    Args:
        date_str: Date string in various formats
    
    Returns:
        ISO formatted date string, or None if parsing fails
    
    Example:
        >>> normalize_date_format("15-11-2023")
        '2023-11-15'
        >>> normalize_date_format("15/11/2023")
        '2023-11-15'
    """
    if not date_str:
        return None
    
    from datetime import datetime
    
    # Common Indian date formats
    formats = [
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%d.%m.%Y',
        '%Y-%m-%d',
        '%d %B %Y',
        '%d %b %Y',
        '%B %d, %Y',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return None


def remove_special_characters(text: str, keep_chars: str = '') -> str:
    """
    Remove special characters from text.
    
    Args:
        text: Input text
        keep_chars: String of characters to keep (in addition to alphanumeric)
    
    Returns:
        Text with special characters removed
    
    Example:
        >>> remove_special_characters("Case@#123!", keep_chars='!')
        'Case123!'
    """
    if not text:
        return ""
    
    # Keep alphanumeric, spaces, and specified characters
    pattern = f'[^\\w\\s{re.escape(keep_chars)}]'
    result = re.sub(pattern, '', text)
    
    return remove_extra_whitespace(result)


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode characters to ASCII equivalents where possible.
    
    Args:
        text: Input text with Unicode characters
    
    Returns:
        Normalized text
    
    Example:
        >>> normalize_unicode("Café")
        'Cafe'
    """
    if not text:
        return ""
    
    # Normalize to NFKD form
    normalized = unicodedata.normalize('NFKD', text)
    
    # Encode to ASCII, ignoring errors
    ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
    
    return ascii_text


def extract_case_type_abbreviation(case_type: str) -> str:
    """
    Extract standard abbreviation for case type.
    
    Args:
        case_type: Full or partial case type name
    
    Returns:
        Standardized abbreviation
    
    Example:
        >>> extract_case_type_abbreviation("Criminal Appeal")
        'CRL.A'
        >>> extract_case_type_abbreviation("Writ Petition")
        'W.P.'
    """
    if not case_type:
        return ""
    
    case_type_upper = case_type.upper()
    
    # Common abbreviations
    mappings = {
        'CRIMINAL APPEAL': 'CRL.A',
        'CIVIL APPEAL': 'C.A',
        'WRIT PETITION': 'W.P',
        'SPECIAL LEAVE PETITION': 'SLP',
        'CIVIL REVISION': 'C.R',
        'CRIMINAL REVISION': 'CRL.REV',
        'BAIL APPLICATION': 'BAIL',
        'EXECUTION PETITION': 'E.P',
        'MISCELLANEOUS': 'MISC',
    }
    
    for full_name, abbr in mappings.items():
        if full_name in case_type_upper:
            return abbr
    
    # Return cleaned version if no mapping found
    return case_type.upper()


def standardize_phone_number(phone: str) -> Optional[str]:
    """
    Standardize Indian phone numbers.
    
    Args:
        phone: Phone number string
    
    Returns:
        Standardized phone number, or None if invalid
    
    Example:
        >>> standardize_phone_number("+91-98765-43210")
        '+919876543210'
    """
    if not phone:
        return None
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Indian mobile numbers are 10 digits
    if len(digits) == 10:
        return f"+91{digits}"
    elif len(digits) == 12 and digits.startswith('91'):
        return f"+{digits}"
    
    return None


def clean_address(address: str) -> str:
    """
    Clean and standardize address text.
    
    Args:
        address: Raw address
    
    Returns:
        Cleaned address
    
    Example:
        >>> clean_address("  123,  Main  Street,\\n New   Delhi - 110001  ")
        '123, Main Street, New Delhi - 110001'
    """
    if not address:
        return ""
    
    # Replace newlines with spaces
    address = address.replace('\n', ' ').replace('\r', ' ')
    
    # Remove extra whitespace
    address = remove_extra_whitespace(address)
    
    # Standardize comma spacing
    address = re.sub(r'\s*,\s*', ', ', address)
    
    return address
