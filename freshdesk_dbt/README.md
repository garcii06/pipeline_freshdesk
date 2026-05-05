# freshdesk_dbt

dbt project for transforming FreshDesk data loaded into Snowflake.

## Stack
- dbt Core + dbt-snowflake
- Snowflake (freshdesk_raw database)

## Structure
models/
├── bronze/    # Raw JSON extraction from source tables
├── silver/    # Cleaned, decoded, business logic
└── gold/      # Aggregated metrics for consumption

## Medallion Layers

**Bronze** — extracts fields from raw JSON, deduplicates by id
**Silver** — decodes status/priority codes, extracts custom fields, drops irrelevant columns  
**Gold** — aggregated metrics served to Power BI

## Sources

Raw data lives in `freshdesk_raw.raw`:
- `tickets` — support tickets
- `companies` — customer companies
- `contacts` — customer contacts

## Setup

Add connection to `~/.dbt/profiles.yml` — see `.env.example` for required Snowflake credentials.

## Commands

```bash
dbt run          # run all models
dbt test         # run all tests
dbt run --select bronze  # run specific layer
```