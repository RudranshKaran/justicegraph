"""
Data models for JusticeGraph Phase 1.

This module defines SQLAlchemy ORM models for all judicial entities
including Courts, Cases, Hearings, Judges, Cause Lists, and Judgments.

All models support JSON serialization and PostgreSQL integration.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Text, 
    ForeignKey, Boolean, Float, JSON, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
import json

Base = declarative_base()


class CaseStatus(enum.Enum):
    """Enumeration of possible case statuses."""
    PENDING = "pending"
    DISPOSED = "disposed"
    WITHDRAWN = "withdrawn"
    DISMISSED = "dismissed"
    DECREED = "decreed"
    ADJOURNED = "adjourned"


class CaseType(enum.Enum):
    """Enumeration of case types in Indian judiciary."""
    CIVIL = "civil"
    CRIMINAL = "criminal"
    WRIT = "writ"
    APPEAL = "appeal"
    REVISION = "revision"
    PETITION = "petition"
    EXECUTION = "execution"
    MISC = "miscellaneous"


class Court(Base):
    """
    Represents a court in the Indian judicial system.
    
    Attributes:
        court_id (int): Primary key, unique identifier for the court
        court_name (str): Official name of the court
        court_code (str): Standardized court code (e.g., "DL-HC" for Delhi High Court)
        court_type (str): Type of court (Supreme Court, High Court, District Court, etc.)
        state (str): State where the court is located
        district (str): District where the court is located (if applicable)
        address (str): Physical address of the court
        jurisdiction (str): Geographic or subject matter jurisdiction
        established_date (date): Date when the court was established
        metadata (JSON): Additional court-specific metadata
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp
    """
    __tablename__ = 'courts'

    court_id = Column(Integer, primary_key=True, autoincrement=True)
    court_name = Column(String(255), nullable=False)
    court_code = Column(String(50), unique=True, nullable=False, index=True)
    court_type = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    jurisdiction = Column(String(255), nullable=True)
    established_date = Column(Date, nullable=True)
    additional_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    cases = relationship("Case", back_populates="court")
    judges = relationship("Judge", back_populates="court")
    cause_lists = relationship("CauseList", back_populates="court")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Court instance to a dictionary for JSON serialization."""
        return {
            'court_id': self.court_id,
            'court_name': self.court_name,
            'court_code': self.court_code,
            'court_type': self.court_type,
            'state': self.state,
            'district': self.district,
            'address': self.address,
            'jurisdiction': self.jurisdiction,
            'established_date': self.established_date.isoformat() if self.established_date is not None else None,
            'additional_metadata': self.additional_metadata,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }


class Judge(Base):
    """
    Represents a judge in the Indian judicial system.
    
    Attributes:
        judge_id (int): Primary key, unique identifier for the judge
        judge_name (str): Full name of the judge
        normalized_name (str): Cleaned and normalized name for matching
        designation (str): Current designation (e.g., Chief Justice, Justice, Additional Judge)
        court_id (int): Foreign key to the court where the judge serves
        appointment_date (date): Date when the judge was appointed
        retirement_date (date): Expected retirement date
        specialization (str): Area of legal specialization (if any)
        is_active (bool): Whether the judge is currently active
        metadata (JSON): Additional judge-specific metadata
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp
    """
    __tablename__ = 'judges'

    judge_id = Column(Integer, primary_key=True, autoincrement=True)
    judge_name = Column(String(255), nullable=False)
    normalized_name = Column(String(255), nullable=False, index=True)
    designation = Column(String(100), nullable=True)
    court_id = Column(Integer, ForeignKey('courts.court_id'), nullable=False, index=True)
    appointment_date = Column(Date, nullable=True)
    retirement_date = Column(Date, nullable=True)
    specialization = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    additional_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    court = relationship("Court", back_populates="judges")
    hearings = relationship("Hearing", back_populates="judge")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Judge instance to a dictionary for JSON serialization."""
        return {
            'judge_id': self.judge_id,
            'judge_name': self.judge_name,
            'normalized_name': self.normalized_name,
            'designation': self.designation,
            'court_id': self.court_id,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date is not None else None,
            'retirement_date': self.retirement_date.isoformat() if self.retirement_date is not None else None,
            'specialization': self.specialization,
            'is_active': self.is_active,
            'additional_metadata': self.additional_metadata,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }


class Case(Base):
    """
    Represents a legal case in the judicial system.
    
    Attributes:
        case_id (int): Primary key, unique identifier for the case
        case_number (str): Official case number (e.g., "CRL.A/123/2023")
        normalized_case_number (str): Standardized case number format "TYPE/NUMBER/YEAR"
        case_type (CaseType): Type of case (civil, criminal, etc.)
        case_status (CaseStatus): Current status of the case
        filing_date (date): Date when the case was filed
        first_hearing_date (date): Date of the first hearing
        last_hearing_date (date): Date of the most recent hearing
        next_hearing_date (date): Date of the next scheduled hearing
        disposal_date (date): Date when the case was disposed (if applicable)
        petitioner (str): Name of the petitioner/plaintiff
        respondent (str): Name of the respondent/defendant
        petitioner_advocate (str): Name of petitioner's advocate
        respondent_advocate (str): Name of respondent's advocate
        court_id (int): Foreign key to the court where the case is filed
        subject_matter (str): Brief description of the case subject
        stage (str): Current stage of the case (e.g., arguments, evidence, judgment)
        is_pending (bool): Whether the case is currently pending
        priority_score (float): AI-generated priority score (for Phase 2)
        metadata (JSON): Additional case-specific metadata
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp
    """
    __tablename__ = 'cases'

    case_id = Column(Integer, primary_key=True, autoincrement=True)
    case_number = Column(String(100), nullable=False)
    normalized_case_number = Column(String(100), nullable=False, index=True)
    case_type = Column(Enum(CaseType), nullable=False, index=True)
    case_status = Column(Enum(CaseStatus), nullable=False, index=True)
    filing_date = Column(Date, nullable=True, index=True)
    first_hearing_date = Column(Date, nullable=True)
    last_hearing_date = Column(Date, nullable=True)
    next_hearing_date = Column(Date, nullable=True, index=True)
    disposal_date = Column(Date, nullable=True)
    petitioner = Column(String(500), nullable=True)
    respondent = Column(String(500), nullable=True)
    petitioner_advocate = Column(String(255), nullable=True)
    respondent_advocate = Column(String(255), nullable=True)
    court_id = Column(Integer, ForeignKey('courts.court_id'), nullable=False, index=True)
    subject_matter = Column(Text, nullable=True)
    stage = Column(String(100), nullable=True)
    is_pending = Column(Boolean, default=True, nullable=False, index=True)
    priority_score = Column(Float, nullable=True)
    additional_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    court = relationship("Court", back_populates="cases")
    hearings = relationship("Hearing", back_populates="case", cascade="all, delete-orphan")
    judgments = relationship("Judgment", back_populates="case")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Case instance to a dictionary for JSON serialization."""
        return {
            'case_id': self.case_id,
            'case_number': self.case_number,
            'normalized_case_number': self.normalized_case_number,
            'case_type': self.case_type.value if self.case_type is not None else None,
            'case_status': self.case_status.value if self.case_status is not None else None,
            'filing_date': self.filing_date.isoformat() if self.filing_date is not None else None,
            'first_hearing_date': self.first_hearing_date.isoformat() if self.first_hearing_date is not None else None,
            'last_hearing_date': self.last_hearing_date.isoformat() if self.last_hearing_date is not None else None,
            'next_hearing_date': self.next_hearing_date.isoformat() if self.next_hearing_date is not None else None,
            'disposal_date': self.disposal_date.isoformat() if self.disposal_date is not None else None,
            'petitioner': self.petitioner,
            'respondent': self.respondent,
            'petitioner_advocate': self.petitioner_advocate,
            'respondent_advocate': self.respondent_advocate,
            'court_id': self.court_id,
            'subject_matter': self.subject_matter,
            'stage': self.stage,
            'is_pending': self.is_pending,
            'priority_score': self.priority_score,
            'additional_metadata': self.additional_metadata,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }


class Hearing(Base):
    """
    Represents a court hearing for a specific case.
    
    Attributes:
        hearing_id (int): Primary key, unique identifier for the hearing
        case_id (int): Foreign key to the case
        hearing_date (date): Scheduled date of the hearing
        hearing_time (str): Scheduled time of the hearing
        judge_id (int): Foreign key to the presiding judge
        court_room (str): Court room number or identifier
        purpose (str): Purpose of the hearing (e.g., arguments, final hearing, evidence)
        outcome (str): Outcome of the hearing (e.g., adjourned, arguments heard, judgment reserved)
        next_hearing_date (date): Date of the next hearing (if adjourned)
        remarks (str): Additional remarks or notes from the hearing
        is_completed (bool): Whether the hearing has been completed
        metadata (JSON): Additional hearing-specific metadata
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp
    """
    __tablename__ = 'hearings'

    hearing_id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey('cases.case_id'), nullable=False, index=True)
    hearing_date = Column(Date, nullable=False, index=True)
    hearing_time = Column(String(50), nullable=True)
    judge_id = Column(Integer, ForeignKey('judges.judge_id'), nullable=True, index=True)
    court_room = Column(String(50), nullable=True)
    purpose = Column(String(255), nullable=True)
    outcome = Column(String(255), nullable=True)
    next_hearing_date = Column(Date, nullable=True)
    remarks = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    additional_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="hearings")
    judge = relationship("Judge", back_populates="hearings")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Hearing instance to a dictionary for JSON serialization."""
        return {
            'hearing_id': self.hearing_id,
            'case_id': self.case_id,
            'hearing_date': self.hearing_date.isoformat() if self.hearing_date is not None else None,
            'hearing_time': self.hearing_time,
            'judge_id': self.judge_id,
            'court_room': self.court_room,
            'purpose': self.purpose,
            'outcome': self.outcome,
            'next_hearing_date': self.next_hearing_date.isoformat() if self.next_hearing_date is not None else None,
            'remarks': self.remarks,
            'is_completed': self.is_completed,
            'additional_metadata': self.additional_metadata,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }


class CauseList(Base):
    """
    Represents a daily cause list (schedule) for a court.
    
    Attributes:
        cause_list_id (int): Primary key, unique identifier for the cause list
        court_id (int): Foreign key to the court
        list_date (date): Date for which the cause list is prepared
        judge_id (int): Foreign key to the presiding judge (if applicable)
        court_room (str): Court room number or identifier
        case_number (str): Case number appearing in the cause list
        case_id (int): Foreign key to the case (if matched)
        serial_number (int): Serial number of the case in the cause list
        hearing_time (str): Scheduled time for the hearing
        case_title (str): Short title or parties of the case
        purpose (str): Purpose of the hearing
        source_url (str): URL of the original cause list
        raw_data (JSON): Raw data from the cause list source
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp
    """
    __tablename__ = 'cause_lists'

    cause_list_id = Column(Integer, primary_key=True, autoincrement=True)
    court_id = Column(Integer, ForeignKey('courts.court_id'), nullable=False, index=True)
    list_date = Column(Date, nullable=False, index=True)
    judge_id = Column(Integer, ForeignKey('judges.judge_id'), nullable=True)
    court_room = Column(String(50), nullable=True)
    case_number = Column(String(100), nullable=False)
    case_id = Column(Integer, ForeignKey('cases.case_id'), nullable=True, index=True)
    serial_number = Column(Integer, nullable=True)
    hearing_time = Column(String(50), nullable=True)
    case_title = Column(String(500), nullable=True)
    purpose = Column(String(255), nullable=True)
    source_url = Column(String(500), nullable=True)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    court = relationship("Court", back_populates="cause_lists")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the CauseList instance to a dictionary for JSON serialization."""
        return {
            'cause_list_id': self.cause_list_id,
            'court_id': self.court_id,
            'list_date': self.list_date.isoformat() if self.list_date is not None else None,
            'judge_id': self.judge_id,
            'court_room': self.court_room,
            'case_number': self.case_number,
            'case_id': self.case_id,
            'serial_number': self.serial_number,
            'hearing_time': self.hearing_time,
            'case_title': self.case_title,
            'purpose': self.purpose,
            'source_url': self.source_url,
            'raw_data': self.raw_data,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }


class Judgment(Base):
    """
    Represents a court judgment or order.
    
    Attributes:
        judgment_id (int): Primary key, unique identifier for the judgment
        case_id (int): Foreign key to the case
        judgment_date (date): Date when the judgment was pronounced
        judge_names (str): Names of judges on the bench (comma-separated)
        judgment_type (str): Type of judgment (final judgment, interim order, etc.)
        judgment_summary (str): Brief summary of the judgment
        judgment_text (str): Full text of the judgment
        result (str): Result of the judgment (allowed, dismissed, etc.)
        citation (str): Legal citation for the judgment
        source_url (str): URL of the judgment document
        pdf_path (str): Local file path to the judgment PDF
        metadata (JSON): Additional judgment-specific metadata
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp
    """
    __tablename__ = 'judgments'

    judgment_id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey('cases.case_id'), nullable=False, index=True)
    judgment_date = Column(Date, nullable=False, index=True)
    judge_names = Column(String(500), nullable=True)
    judgment_type = Column(String(100), nullable=True)
    judgment_summary = Column(Text, nullable=True)
    judgment_text = Column(Text, nullable=True)
    result = Column(String(100), nullable=True)
    citation = Column(String(255), nullable=True)
    source_url = Column(String(500), nullable=True)
    pdf_path = Column(String(500), nullable=True)
    additional_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    case = relationship("Case", back_populates="judgments")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Judgment instance to a dictionary for JSON serialization."""
        return {
            'judgment_id': self.judgment_id,
            'case_id': self.case_id,
            'judgment_date': self.judgment_date.isoformat() if self.judgment_date is not None else None,
            'judge_names': self.judge_names,
            'judgment_type': self.judgment_type,
            'judgment_summary': self.judgment_summary,
            'judgment_text': self.judgment_text,
            'result': self.result,
            'citation': self.citation,
            'source_url': self.source_url,
            'pdf_path': self.pdf_path,
            'additional_metadata': self.additional_metadata,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }
