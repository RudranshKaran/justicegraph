# JusticeGraph Data Dictionary

## Overview

This document describes all data entities, their fields, data types, constraints, and relationships in the JusticeGraph database.

---

## Entity: **Court**

Represents a court in the Indian judicial system.

| Field Name | Data Type | Nullable | Description | Example |
|------------|-----------|----------|-------------|---------|
| `court_id` | Integer (PK) | No | Unique identifier for the court | 1 |
| `court_name` | String(255) | No | Official name of the court | "Delhi High Court" |
| `court_code` | String(50) | No | Standardized court code (unique) | "DL-HC" |
| `court_type` | String(100) | No | Type of court | "High Court" |
| `state` | String(100) | No | State where court is located | "Delhi" |
| `district` | String(100) | Yes | District (for district courts) | "Central Delhi" |
| `address` | Text | Yes | Physical address | "Sher Shah Road, New Delhi" |
| `jurisdiction` | String(255) | Yes | Jurisdiction description | "Delhi NCT" |
| `established_date` | Date | Yes | Date when court was established | 2000-01-15 |
| `metadata` | JSON | Yes | Additional court-specific data | {...} |
| `created_at` | DateTime | No | Record creation timestamp | 2023-11-15T10:30:00 |
| `updated_at` | DateTime | No | Last update timestamp | 2023-11-15T10:30:00 |

**Relationships:**
- One court has many cases
- One court has many judges
- One court has many cause lists

---

## Entity: **Judge**

Represents a judge in the Indian judicial system.

| Field Name | Data Type | Nullable | Description | Example |
|------------|-----------|----------|-------------|---------|
| `judge_id` | Integer (PK) | No | Unique identifier | 1 |
| `judge_name` | String(255) | No | Full name | "Justice S. Ravindra Bhat" |
| `normalized_name` | String(255) | No | Cleaned name (for matching) | "S. Ravindra Bhat" |
| `designation` | String(100) | Yes | Current designation | "Chief Justice" |
| `court_id` | Integer (FK) | No | Court where judge serves | 1 |
| `appointment_date` | Date | Yes | Appointment date | 2015-06-01 |
| `retirement_date` | Date | Yes | Expected retirement date | 2027-05-31 |
| `specialization` | String(255) | Yes | Legal specialization | "Constitutional Law" |
| `is_active` | Boolean | No | Currently serving? | true |
| `metadata` | JSON | Yes | Additional information | {...} |
| `created_at` | DateTime | No | Record creation timestamp | 2023-11-15T10:30:00 |
| `updated_at` | DateTime | No | Last update timestamp | 2023-11-15T10:30:00 |

**Relationships:**
- One judge belongs to one court
- One judge presides over many hearings

---

## Entity: **Case**

Represents a legal case in the judicial system.

| Field Name | Data Type | Nullable | Description | Example |
|------------|-----------|----------|-------------|---------|
| `case_id` | Integer (PK) | No | Unique identifier | 1 |
| `case_number` | String(100) | No | Official case number | "CRL.A/123/2023" |
| `normalized_case_number` | String(100) | No | Standardized format | "CRL.A/123/2023" |
| `case_type` | Enum | No | Type of case | CRIMINAL, CIVIL, WRIT |
| `case_status` | Enum | No | Current status | PENDING, DISPOSED |
| `filing_date` | Date | Yes | Date case was filed | 2023-01-15 |
| `first_hearing_date` | Date | Yes | First hearing date | 2023-02-01 |
| `last_hearing_date` | Date | Yes | Most recent hearing | 2023-11-14 |
| `next_hearing_date` | Date | Yes | Next scheduled hearing | 2023-12-01 |
| `disposal_date` | Date | Yes | Disposal date (if closed) | null |
| `petitioner` | String(500) | Yes | Petitioner/Plaintiff name | "State of Delhi" |
| `respondent` | String(500) | Yes | Respondent/Defendant name | "Ram Kumar" |
| `petitioner_advocate` | String(255) | Yes | Petitioner's lawyer | "Adv. Sharma" |
| `respondent_advocate` | String(255) | Yes | Respondent's lawyer | "Adv. Verma" |
| `court_id` | Integer (FK) | No | Court where case is filed | 1 |
| `subject_matter` | Text | Yes | Brief description | "Murder case under IPC 302" |
| `stage` | String(100) | Yes | Current stage | "Arguments" |
| `is_pending` | Boolean | No | Is case currently pending? | true |
| `priority_score` | Float | Yes | AI-generated priority | 0.85 |
| `metadata` | JSON | Yes | Additional case data | {...} |
| `created_at` | DateTime | No | Record creation | 2023-11-15T10:30:00 |
| `updated_at` | DateTime | No | Last update | 2023-11-15T10:30:00 |

**Relationships:**
- One case belongs to one court
- One case has many hearings
- One case has many judgments

**Enums:**
- `case_type`: CIVIL, CRIMINAL, WRIT, APPEAL, REVISION, PETITION, EXECUTION, MISC
- `case_status`: PENDING, DISPOSED, WITHDRAWN, DISMISSED, DECREED, ADJOURNED

---

## Entity: **Hearing**

Represents a court hearing for a specific case.

| Field Name | Data Type | Nullable | Description | Example |
|------------|-----------|----------|-------------|---------|
| `hearing_id` | Integer (PK) | No | Unique identifier | 1 |
| `case_id` | Integer (FK) | No | Associated case | 1 |
| `hearing_date` | Date | No | Date of hearing | 2023-11-15 |
| `hearing_time` | String(50) | Yes | Scheduled time | "10:30 AM" |
| `judge_id` | Integer (FK) | Yes | Presiding judge | 1 |
| `court_room` | String(50) | Yes | Court room number | "Court 3" |
| `purpose` | String(255) | Yes | Purpose of hearing | "Final Arguments" |
| `outcome` | String(255) | Yes | Hearing outcome | "Adjourned to 01-12-2023" |
| `next_hearing_date` | Date | Yes | Next hearing date | 2023-12-01 |
| `remarks` | Text | Yes | Additional notes | "Defense counsel absent" |
| `is_completed` | Boolean | No | Hearing completed? | true |
| `metadata` | JSON | Yes | Additional data | {...} |
| `created_at` | DateTime | No | Record creation | 2023-11-15T10:30:00 |
| `updated_at` | DateTime | No | Last update | 2023-11-15T10:30:00 |

**Relationships:**
- One hearing belongs to one case
- One hearing has one judge presiding

---

## Entity: **CauseList**

Represents a daily cause list (hearing schedule) for a court.

| Field Name | Data Type | Nullable | Description | Example |
|------------|-----------|----------|-------------|---------|
| `cause_list_id` | Integer (PK) | No | Unique identifier | 1 |
| `court_id` | Integer (FK) | No | Court for this list | 1 |
| `list_date` | Date | No | Date of the cause list | 2023-11-15 |
| `judge_id` | Integer (FK) | Yes | Presiding judge (if specified) | 1 |
| `court_room` | String(50) | Yes | Court room | "Court 3" |
| `case_number` | String(100) | No | Case number in list | "CRL.A/123/2023" |
| `case_id` | Integer (FK) | Yes | Linked case (if matched) | 1 |
| `serial_number` | Integer | Yes | Serial in the list | 5 |
| `hearing_time` | String(50) | Yes | Scheduled time | "10:30 AM" |
| `case_title` | String(500) | Yes | Short case title | "State v. Ram Kumar" |
| `purpose` | String(255) | Yes | Purpose of listing | "Arguments" |
| `source_url` | String(500) | Yes | Original URL | "https://..." |
| `raw_data` | JSON | Yes | Raw cause list data | {...} |
| `created_at` | DateTime | No | Record creation | 2023-11-15T10:30:00 |
| `updated_at` | DateTime | No | Last update | 2023-11-15T10:30:00 |

**Relationships:**
- One cause list entry belongs to one court
- May link to one case (if matched)

---

## Entity: **Judgment**

Represents a court judgment or order.

| Field Name | Data Type | Nullable | Description | Example |
|------------|-----------|----------|-------------|---------|
| `judgment_id` | Integer (PK) | No | Unique identifier | 1 |
| `case_id` | Integer (FK) | No | Associated case | 1 |
| `judgment_date` | Date | No | Judgment pronounced date | 2023-11-15 |
| `judge_names` | String(500) | Yes | Judges on bench (comma-separated) | "Justice A, Justice B" |
| `judgment_type` | String(100) | Yes | Type of judgment | "Final Judgment" |
| `judgment_summary` | Text | Yes | Brief summary | "Appeal dismissed" |
| `judgment_text` | Text | Yes | Full judgment text | "..." |
| `result` | String(100) | Yes | Result | "Dismissed" |
| `citation` | String(255) | Yes | Legal citation | "2023 DLT 123" |
| `source_url` | String(500) | Yes | Document URL | "https://..." |
| `pdf_path` | String(500) | Yes | Local PDF path | "data/bronze/..." |
| `metadata` | JSON | Yes | Additional data | {...} |
| `created_at` | DateTime | No | Record creation | 2023-11-15T10:30:00 |
| `updated_at` | DateTime | No | Last update | 2023-11-15T10:30:00 |

**Relationships:**
- One judgment belongs to one case

---

## Data Quality Rules

1. **Uniqueness**: Court codes and case numbers must be unique
2. **Referential Integrity**: All foreign keys must reference valid records
3. **Date Logic**: `disposal_date` must be after `filing_date`
4. **Required Fields**: Case number, court_id, and case_type are mandatory
5. **Enums**: Case type and status must use predefined values
6. **Normalization**: Names and case numbers should be normalized before insertion

---

## Indexes

Performance indexes are created on:
- `court_code` (unique)
- `normalized_case_number`
- `case_status`, `case_type`
- `filing_date`, `next_hearing_date`
- `is_pending`
- `list_date`

---

## Metadata Fields

All entities support a `metadata` JSON field for storing additional, unstructured information specific to data sources or use cases.

---

**Last Updated**: 2023-11-15  
**Version**: 1.0
