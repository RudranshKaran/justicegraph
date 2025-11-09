# JusticeGraph Phase 1 Pipeline Overview

## Architecture

JusticeGraph Phase 1 implements a **medallion architecture** ETL pipeline with three data layers:

### Data Layers

```
┌─────────────────────────────────────────────────────────┐
│  BRONZE LAYER (Raw Data)                                │
│  - HTML cause lists from court websites                 │
│  - PDF judgments                                        │
│  - JSON API responses                                   │
│  - Metadata: source URL, timestamp, fetch parameters   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  SILVER LAYER (Structured Data)                         │
│  - Parsed DataFrames (CSV/JSON)                         │
│  - Extracted fields: case numbers, parties, dates       │
│  - Basic cleaning: whitespace removal, encoding fixes   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  GOLD LAYER (Analysis-Ready Data)                       │
│  - Normalized entities                                  │
│  - Standardized case numbers, names, dates              │
│  - Resolved references (court IDs, judge IDs)           │
│  - Loaded into PostgreSQL database                      │
└─────────────────────────────────────────────────────────┘
```

---

## Pipeline Stages

### 1. **INGEST** (Bronze Layer)

**Module**: `ingest/`

**Purpose**: Fetch raw data from judicial websites and APIs

**Components**:
- `cause_list_ingest.py`: Scrape daily hearing schedules
- `case_status_ingest.py`: Fetch individual case details
- `judgment_ingest.py`: Download judgment documents (PDF/HTML)

**Key Features**:
- HTTP retry logic with exponential backoff
- Rate limiting to respect website terms
- Metadata tracking (source URL, timestamp)
- Error handling and logging

**Output**: Raw files in `data/bronze/` with accompanying metadata JSON files

---

### 2. **PARSE** (Silver Layer)

**Module**: `parse/`

**Purpose**: Extract structured data from raw HTML/PDF files

**Components**:
- `parse_cause_list.py`: Parse HTML tables into DataFrames
- `parse_case_status.py`: Extract case details from HTML
- `parse_judgment.py`: Extract text from PDF judgments

**Key Features**:
- BeautifulSoup HTML parsing
- Pattern matching for case numbers
- Extraction of parties, advocates, dates
- DataFrame output (CSV + JSON)

**Output**: Structured CSV/JSON files in `data/silver/`

---

### 3. **NORMALIZE** (Gold Layer)

**Module**: `normalize/`

**Purpose**: Clean and standardize data for consistency

**Components**:
- `clean_text_utils.py`: Text cleaning functions
- `normalize_entities.py`: Entity normalization

**Key Features**:
- Remove honorifics (Hon'ble, Justice, Adv.)
- Standardize case numbers (TYPE/NUMBER/YEAR format)
- Normalize names (proper case, whitespace)
- Date format standardization (ISO 8601)

**Output**: Cleaned CSV files in `data/gold/`

---

### 4. **VALIDATE** (Quality Checks)

**Module**: `validation/`

**Purpose**: Ensure data quality before database loading

**Components**:
- `data_validation.py`: Validation rules and checks

**Validation Checks**:
- ✓ Required fields are not null
- ✓ Date formats are valid
- ✓ Case numbers follow standard pattern
- ✓ No duplicate records
- ✓ Referential integrity (foreign keys)

**Output**: Validation reports in `logs/`

---

### 5. **LOAD** (Database)

**Module**: `utils/db_utils.py`

**Purpose**: Insert data into PostgreSQL database

**Key Features**:
- Upsert operations (insert or update)
- Transaction management
- Connection pooling
- Error handling and rollback

**Output**: Populated database tables

---

## Workflow Orchestration

### Prefect Integration

JusticeGraph uses **Prefect** for workflow orchestration:

```python
from pipelines.phase1_pipeline import run_phase1_pipeline

# Run the complete pipeline
run_phase1_pipeline(
    court_code='DL-HC',
    start_date='2023-11-01',
    end_date='2023-11-07'
)
```

### Pipeline Execution Flow

```
START
  │
  ├─→ Task: ingest_cause_lists()
  │     ├─ Fetch HTML from court website
  │     ├─ Save to bronze layer
  │     └─ Return file paths
  │
  ├─→ Task: parse_cause_lists()
  │     ├─ Parse HTML tables
  │     ├─ Extract structured data
  │     └─ Save to silver layer
  │
  ├─→ Task: normalize_data()
  │     ├─ Clean text fields
  │     ├─ Standardize formats
  │     └─ Save to gold layer
  │
  ├─→ Task: validate_data()
  │     ├─ Run quality checks
  │     ├─ Log validation results
  │     └─ Return pass/fail status
  │
  ├─→ Task: load_to_database()
  │     ├─ Convert to ORM objects
  │     ├─ Insert/upsert to PostgreSQL
  │     └─ Return record count
  │
END
```

---

## Data Models

### Entity Relationship Diagram

```
┌─────────────┐
│   Court     │
│─────────────│
│ court_id PK │◄──┐
│ court_code  │   │
│ court_name  │   │
└─────────────┘   │
                  │
       ┌──────────┴──────────┐
       │                     │
┌──────▼──────┐       ┌──────▼──────┐
│   Judge     │       │    Case     │
│─────────────│       │─────────────│
│ judge_id PK │◄──┐   │ case_id PK  │◄──┐
│ court_id FK │   │   │ court_id FK │   │
│ judge_name  │   │   │ case_number │   │
└─────────────┘   │   │ status      │   │
                  │   └─────────────┘   │
                  │                     │
           ┌──────┴──────┐       ┌──────┴──────┐
           │             │       │             │
    ┌──────▼──────┐ ┌────▼─────────┐ ┌────────▼────────┐
    │  Hearing    │ │  CauseList   │ │   Judgment      │
    │─────────────│ │──────────────│ │─────────────────│
    │ hearing_id  │ │ cause_list_id│ │ judgment_id     │
    │ case_id FK  │ │ court_id FK  │ │ case_id FK      │
    │ judge_id FK │ │ case_id FK   │ │ judgment_date   │
    │ date        │ │ list_date    │ │ result          │
    └─────────────┘ └──────────────┘ └─────────────────┘
```

---

## Logging and Monitoring

### Structured Logging

All operations are logged in JSON format:

```json
{
  "timestamp": "2023-11-15T14:30:22.123Z",
  "level": "INFO",
  "logger": "ingest",
  "message": "Scraper completed successfully",
  "scraper_name": "cause_list_ingest",
  "court_code": "DL-HC",
  "record_count": 150,
  "status": "success",
  "duration_seconds": 12.5
}
```

### Log Files

- `logs/ingest.log`: Scraping activities
- `logs/parse.log`: Parsing operations
- `logs/pipeline.log`: Pipeline execution
- `logs/validation.log`: Data quality checks

---

## Configuration

### Environment Variables (`configs/settings.env`)

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/justicegraph
LOG_LEVEL=INFO
REQUEST_TIMEOUT=60
RATE_LIMIT_DELAY=2.0
```

### Data Sources (`configs/sources.yaml`)

```yaml
sources:
  - name: "Delhi High Court"
    code: "DL-HC"
    base_url: "https://delhihighcourt.nic.in"
    update_frequency: "daily"
    active: true
```

---

## Error Handling

### Retry Strategy

- HTTP requests: 3 retries with exponential backoff
- Database operations: Transaction rollback on error
- Pipeline tasks: Graceful failure with logging

### Error Logging

```python
logger.error(f"Failed to fetch {url}: {error}")
log_scraper_activity(
    logger,
    'cause_list_ingest',
    url,
    'failed',
    errors=['Connection timeout']
)
```

---

## Performance Optimization

### Strategies

1. **Connection Pooling**: Database connection reuse
2. **Rate Limiting**: Respect website terms of service
3. **Parallel Processing**: Multiple workers (future enhancement)
4. **Incremental Updates**: Only fetch new data
5. **Indexed Queries**: Database indexes on key fields

### Benchmarks

- Ingest: ~2-3 seconds per cause list
- Parse: ~1 second per HTML file
- Normalize: ~0.5 seconds per 100 records
- Load: ~0.1 seconds per 100 records

---

## Extensibility

### Adding New Data Sources

1. Create scraper in `ingest/new_source_ingest.py`
2. Create parser in `parse/parse_new_source.py`
3. Add source metadata to `configs/sources.yaml`
4. Update pipeline to include new source

### Adding New Validations

1. Add validation function in `validation/data_validation.py`
2. Call from `validate_data()` task
3. Log results with `log_validation_results()`

---

## Deployment

### Local Development

```bash
python setup.py
python test_pipeline.py
python pipelines/phase1_pipeline.py DL-HC 2023-11-01 2023-11-07
```

### Production Deployment

1. Set up PostgreSQL database
2. Configure environment variables
3. Set up Prefect server (optional)
4. Schedule daily runs via cron or Prefect
5. Monitor logs and set up alerts

---

## Maintenance

### Daily Tasks

- Monitor pipeline execution logs
- Check validation reports
- Review error counts

### Weekly Tasks

- Archive old bronze layer files
- Review and update data sources
- Check database growth

### Monthly Tasks

- Performance optimization review
- Update documentation
- Security audit

---

## Future Enhancements (Phase 2)

- AI-driven case prioritization
- Backlog prediction models
- Judge workload analysis
- Interactive dashboards
- REST API for data access
- Real-time data updates

---

**Version**: 1.0  
**Last Updated**: November 6, 2025  
**Maintained by**: JusticeGraph Team
