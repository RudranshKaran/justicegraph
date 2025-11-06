"""
Database utilities for JusticeGraph.

Provides functions for connecting to PostgreSQL, executing queries,
and performing CRUD operations on judicial data models.
"""

import os
from typing import Any, Dict, List, Optional, Union, Iterator
from contextlib import contextmanager
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pathlib import Path
import logging

# Add models directory to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.data_models import Base, Court, Judge, Case, Hearing, CauseList, Judgment

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manager class for database operations.
    
    Handles connection pooling, session management, and common database
    operations for JusticeGraph entities.
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            connection_string: SQLAlchemy connection string
                             If None, reads from DATABASE_URL environment variable
        
        Example:
            >>> db = DatabaseManager("postgresql://user:pass@localhost:5432/justicegraph")
            >>> db.create_tables()
        """
        if connection_string is None:
            connection_string = os.getenv('DATABASE_URL', 'sqlite:///justicegraph.db')
        
        self.engine = create_engine(
            connection_string,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True,  # Verify connections before using
            pool_size=5,
            max_overflow=10
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"Database manager initialized with connection: {connection_string}")
    
    def create_tables(self):
        """
        Create all tables defined in the data models.
        
        Example:
            >>> db = DatabaseManager()
            >>> db.create_tables()
        """
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def drop_tables(self):
        """
        Drop all tables. Use with caution!
        
        Example:
            >>> db = DatabaseManager()
            >>> db.drop_tables()
        """
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error dropping database tables: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Iterator[Session]:
        """
        Context manager for database sessions.
        
        Automatically commits on success and rolls back on error.
        
        Example:
            >>> db = DatabaseManager()
            >>> with db.get_session() as session:
            ...     court = Court(court_name="Delhi HC", court_code="DL-HC")
            ...     session.add(court)
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            session.close()
    
    def insert_record(self, record: Any) -> Optional[int]:
        """
        Insert a single record into the database.
        
        Args:
            record: SQLAlchemy model instance
        
        Returns:
            ID of the inserted record, or None if error occurred
        
        Example:
            >>> db = DatabaseManager()
            >>> court = Court(court_name="Delhi HC", court_code="DL-HC")
            >>> court_id = db.insert_record(court)
        """
        try:
            with self.get_session() as session:
                session.add(record)
                session.flush()
                record_id = record.__dict__[f"{record.__tablename__[:-1]}_id"]
                logger.info(f"Inserted record into {record.__tablename__} with ID {record_id}")
                return record_id
        except IntegrityError as e:
            logger.warning(f"Integrity error inserting into {record.__tablename__}: {e}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error inserting into {record.__tablename__}: {e}")
            return None
    
    def insert_many(self, records: List[Any]) -> int:
        """
        Insert multiple records into the database.
        
        Args:
            records: List of SQLAlchemy model instances
        
        Returns:
            Number of records successfully inserted
        
        Example:
            >>> db = DatabaseManager()
            >>> cases = [Case(...), Case(...), Case(...)]
            >>> count = db.insert_many(cases)
        """
        if not records:
            return 0
        
        inserted_count = 0
        try:
            with self.get_session() as session:
                session.add_all(records)
                session.flush()
                inserted_count = len(records)
                table_name = records[0].__tablename__
                logger.info(f"Inserted {inserted_count} records into {table_name}")
        except SQLAlchemyError as e:
            logger.error(f"Error inserting multiple records: {e}")
        
        return inserted_count
    
    def upsert_record(self, record: Any, unique_keys: List[str]) -> Optional[int]:
        """
        Insert or update a record based on unique keys.
        
        Args:
            record: SQLAlchemy model instance
            unique_keys: List of field names that uniquely identify the record
        
        Returns:
            ID of the upserted record, or None if error occurred
        
        Example:
            >>> db = DatabaseManager()
            >>> court = Court(court_code="DL-HC", court_name="Delhi High Court")
            >>> court_id = db.upsert_record(court, unique_keys=['court_code'])
        """
        try:
            with self.get_session() as session:
                # Build query filter
                model_class = type(record)
                filters = {}
                for key in unique_keys:
                    filters[key] = getattr(record, key)
                
                # Check if record exists
                existing = session.query(model_class).filter_by(**filters).first()
                
                if existing:
                    # Update existing record
                    for key, value in record.__dict__.items():
                        if not key.startswith('_') and key not in ['created_at']:
                            setattr(existing, key, value)
                    session.flush()
                    record_id = existing.__dict__[f"{record.__tablename__[:-1]}_id"]
                    logger.info(f"Updated record in {record.__tablename__} with ID {record_id}")
                else:
                    # Insert new record
                    session.add(record)
                    session.flush()
                    record_id = record.__dict__[f"{record.__tablename__[:-1]}_id"]
                    logger.info(f"Inserted new record into {record.__tablename__} with ID {record_id}")
                
                return record_id
                
        except SQLAlchemyError as e:
            logger.error(f"Error upserting into {record.__tablename__}: {e}")
            return None
    
    def query_by_id(self, model_class: type, record_id: int) -> Optional[Any]:
        """
        Query a record by its ID.
        
        Args:
            model_class: SQLAlchemy model class
            record_id: ID of the record
        
        Returns:
            Model instance if found, None otherwise
        
        Example:
            >>> db = DatabaseManager()
            >>> court = db.query_by_id(Court, 1)
        """
        try:
            with self.get_session() as session:
                id_column_name = f"{model_class.__tablename__[:-1]}_id"
                record = session.query(model_class).filter(
                    getattr(model_class, id_column_name) == record_id
                ).first()
                if record:
                    # Expunge to detach from session so it can be used after session closes
                    session.expunge(record)
                return record
        except SQLAlchemyError as e:
            logger.error(f"Error querying {model_class.__tablename__} by ID {record_id}: {e}")
            return None
    
    def query_by_filter(
        self,
        model_class: type,
        filters: Dict[str, Any],
        limit: Optional[int] = None
    ) -> List[Any]:
        """
        Query records by filter conditions.
        
        Args:
            model_class: SQLAlchemy model class
            filters: Dictionary of field names and values to filter by
            limit: Maximum number of records to return
        
        Returns:
            List of model instances matching the filter
        
        Example:
            >>> db = DatabaseManager()
            >>> cases = db.query_by_filter(
            ...     Case,
            ...     {'court_id': 1, 'is_pending': True},
            ...     limit=10
            ... )
        """
        try:
            with self.get_session() as session:
                query = session.query(model_class).filter_by(**filters)
                if limit:
                    query = query.limit(limit)
                records = query.all()
                # Expunge all records to detach from session
                for record in records:
                    session.expunge(record)
                logger.info(f"Found {len(records)} records in {model_class.__tablename__}")
                return records
        except SQLAlchemyError as e:
            logger.error(f"Error querying {model_class.__tablename__}: {e}")
            return []
    
    def execute_raw_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Execute a raw SQL query and return results.
        
        Args:
            query: SQL query string
            params: Optional parameters for the query
        
        Returns:
            List of dictionaries containing query results
        
        Example:
            >>> db = DatabaseManager()
            >>> results = db.execute_raw_query(
            ...     "SELECT court_name, COUNT(*) as case_count "
            ...     "FROM cases JOIN courts ON cases.court_id = courts.court_id "
            ...     "GROUP BY court_name"
            ... )
        """
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})
                rows = [dict(row._mapping) for row in result]
                logger.info(f"Raw query returned {len(rows)} rows")
                return rows
        except SQLAlchemyError as e:
            logger.error(f"Error executing raw query: {e}")
            return []
    
    def get_table_count(self, model_class: type) -> int:
        """
        Get the total number of records in a table.
        
        Args:
            model_class: SQLAlchemy model class
        
        Returns:
            Number of records in the table
        
        Example:
            >>> db = DatabaseManager()
            >>> count = db.get_table_count(Case)
            >>> print(f"Total cases: {count}")
        """
        try:
            with self.get_session() as session:
                count = session.query(model_class).count()
                logger.info(f"Table {model_class.__tablename__} has {count} records")
                return count
        except SQLAlchemyError as e:
            logger.error(f"Error counting records in {model_class.__tablename__}: {e}")
            return 0


def get_database_manager() -> DatabaseManager:
    """
    Factory function to get a DatabaseManager instance.
    
    Returns:
        DatabaseManager instance configured from environment
    
    Example:
        >>> db = get_database_manager()
        >>> db.create_tables()
    """
    return DatabaseManager()
