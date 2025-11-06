"""
Input/Output utilities for JusticeGraph.

Provides functions for reading, writing, and managing data files
across bronze, silver, and gold layers.
"""

import os
import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def get_data_path(layer: str, filename: str = "") -> Path:
    """
    Get the full path to a file in the data directory.
    
    Args:
        layer: Data layer ('bronze', 'silver', or 'gold')
        filename: Name of the file (optional)
    
    Returns:
        Path object pointing to the file or directory
    
    Example:
        >>> path = get_data_path('bronze', 'cause_list_20231115.html')
        >>> print(path)
        c:/Users/rudra/Desktop/projects/justicegraph/data/bronze/cause_list_20231115.html
    """
    data_dir = PROJECT_ROOT / 'data' / layer
    if filename:
        return data_dir / filename
    return data_dir


def ensure_directory_exists(path: Union[str, Path]) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
    
    Example:
        >>> ensure_directory_exists('data/bronze/2023/11')
    """
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {path}")


def save_json(data: Any, filepath: Union[str, Path], indent: int = 2) -> bool:
    """
    Save data as JSON file.
    
    Args:
        data: Data to save (must be JSON serializable)
        filepath: Path where the file should be saved
        indent: JSON indentation level
    
    Returns:
        True if successful, False otherwise
    
    Example:
        >>> data = {'court': 'Delhi HC', 'cases': 150}
        >>> save_json(data, 'data/silver/court_info.json')
    """
    try:
        filepath = Path(filepath)
        ensure_directory_exists(filepath.parent)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        
        logger.info(f"Successfully saved JSON to {filepath}")
        return True
        
    except (IOError, TypeError) as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
        return False


def load_json(filepath: Union[str, Path]) -> Optional[Any]:
    """
    Load data from a JSON file.
    
    Args:
        filepath: Path to the JSON file
    
    Returns:
        Loaded data, or None if error occurred
    
    Example:
        >>> data = load_json('data/silver/court_info.json')
    """
    try:
        filepath = Path(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Successfully loaded JSON from {filepath}")
        return data
        
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        return None


def save_text(content: str, filepath: Union[str, Path], encoding: str = 'utf-8') -> bool:
    """
    Save text content to a file.
    
    Args:
        content: Text content to save
        filepath: Path where the file should be saved
        encoding: Text encoding (default: utf-8)
    
    Returns:
        True if successful, False otherwise
    
    Example:
        >>> html = "<html><body>Cause List</body></html>"
        >>> save_text(html, 'data/bronze/cause_list.html')
    """
    try:
        filepath = Path(filepath)
        ensure_directory_exists(filepath.parent)
        
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        
        logger.info(f"Successfully saved text to {filepath}")
        return True
        
    except IOError as e:
        logger.error(f"Error saving text to {filepath}: {e}")
        return False


def load_text(filepath: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
    """
    Load text content from a file.
    
    Args:
        filepath: Path to the text file
        encoding: Text encoding (default: utf-8)
    
    Returns:
        Text content, or None if error occurred
    
    Example:
        >>> html = load_text('data/bronze/cause_list.html')
    """
    try:
        filepath = Path(filepath)
        with open(filepath, 'r', encoding=encoding) as f:
            content = f.read()
        
        logger.info(f"Successfully loaded text from {filepath}")
        return content
        
    except IOError as e:
        logger.error(f"Error loading text from {filepath}: {e}")
        return None


def save_with_metadata(
    data: Any,
    filepath: Union[str, Path],
    source: str,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Save data along with metadata (source, timestamp, etc.).
    
    Args:
        data: Data to save
        filepath: Path where the file should be saved
        source: Source of the data (URL, API endpoint, etc.)
        metadata: Additional metadata dictionary
    
    Returns:
        True if successful, False otherwise
    
    Example:
        >>> data = {"cases": [...]}
        >>> save_with_metadata(
        ...     data,
        ...     'data/bronze/cases.json',
        ...     'https://ecourts.gov.in/api/cases'
        ... )
    """
    metadata_dict = {
        'source': source,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }
    
    if metadata:
        metadata_dict.update(metadata)
    
    return save_json(metadata_dict, filepath)


def generate_filename(
    prefix: str,
    extension: str = 'json',
    include_timestamp: bool = True,
    additional_parts: Optional[List[str]] = None
) -> str:
    """
    Generate a standardized filename with optional timestamp.
    
    Args:
        prefix: Prefix for the filename (e.g., 'cause_list', 'case_status')
        extension: File extension without the dot
        include_timestamp: Whether to include timestamp in filename
        additional_parts: Additional parts to include in the filename
    
    Returns:
        Generated filename
    
    Example:
        >>> filename = generate_filename('cause_list', 'html', additional_parts=['DL_HC'])
        >>> print(filename)
        'cause_list_DL_HC_20231115_143022.html'
    """
    parts = [prefix]
    
    if additional_parts:
        parts.extend(additional_parts)
    
    if include_timestamp:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        parts.append(timestamp)
    
    filename = '_'.join(parts) + f'.{extension}'
    return filename


def list_files_in_directory(
    directory: Union[str, Path],
    pattern: str = '*',
    recursive: bool = False
) -> List[Path]:
    """
    List all files in a directory matching a pattern.
    
    Args:
        directory: Directory path
        pattern: File pattern (e.g., '*.json', 'cause_list_*.html')
        recursive: Whether to search recursively in subdirectories
    
    Returns:
        List of Path objects for matching files
    
    Example:
        >>> files = list_files_in_directory('data/bronze', pattern='*.html')
        >>> for file in files:
        ...     print(file.name)
    """
    directory = Path(directory)
    
    if not directory.exists():
        logger.warning(f"Directory does not exist: {directory}")
        return []
    
    if recursive:
        files = list(directory.rglob(pattern))
    else:
        files = list(directory.glob(pattern))
    
    # Filter to only include files (not directories)
    files = [f for f in files if f.is_file()]
    
    logger.info(f"Found {len(files)} files in {directory} matching pattern '{pattern}'")
    return files


def get_file_metadata(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Get metadata about a file (size, creation time, modification time).
    
    Args:
        filepath: Path to the file
    
    Returns:
        Dictionary containing file metadata
    
    Example:
        >>> metadata = get_file_metadata('data/bronze/cause_list.html')
        >>> print(f"File size: {metadata['size_bytes']} bytes")
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        logger.warning(f"File does not exist: {filepath}")
        return {}
    
    stat = filepath.stat()
    
    return {
        'filename': filepath.name,
        'path': str(filepath),
        'size_bytes': stat.st_size,
        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }


def archive_old_files(
    directory: Union[str, Path],
    archive_dir: Union[str, Path],
    days_old: int = 30,
    pattern: str = '*'
) -> int:
    """
    Move old files to an archive directory.
    
    Args:
        directory: Source directory
        archive_dir: Archive directory
        days_old: Files older than this many days will be archived
        pattern: File pattern to match
    
    Returns:
        Number of files archived
    
    Example:
        >>> count = archive_old_files('data/bronze', 'data/archive', days_old=30)
        >>> print(f"Archived {count} files")
    """
    import shutil
    from datetime import timedelta
    
    directory = Path(directory)
    archive_dir = Path(archive_dir)
    ensure_directory_exists(archive_dir)
    
    cutoff_time = datetime.now() - timedelta(days=days_old)
    files = list_files_in_directory(directory, pattern=pattern)
    
    archived_count = 0
    for file in files:
        file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
        
        if file_mtime < cutoff_time:
            destination = archive_dir / file.name
            shutil.move(str(file), str(destination))
            logger.info(f"Archived {file} to {destination}")
            archived_count += 1
    
    logger.info(f"Archived {archived_count} files from {directory}")
    return archived_count
