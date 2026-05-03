# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

**Run the application:**
```bash
streamlit run main.py
```

The app starts at `http://localhost:8501` with 4 pages accessible via sidebar navigation.

## Project Overview

A Streamlit-based **Data Migration Tool** for managing portfolio data migration with table extraction, SQL generation, execution, and history tracking. The core workflow is:

1. User inputs a SQL query
2. LLM extracts table names from the query (using LangChain/LanGraph)
3. App auto-generates DELETE/INSERT statements for data migration
4. User can edit SQL statements
5. User executes individual or bulk SQL operations
6. System tracks migration history and validation results

## Architecture

### Database (SQLite)
Located at `data_migration.db`, initialized by `modules/db_manager.py:init_db()`. Seven tables:

- **migration_jobs**: Top-level migration task records
- **migration_details**: Per-table execution records (delete/insert SQL, status, affected rows)
- **migration_validation**: Data row count validation after migration
- **pfo_stck_ma**: Source portfolio stock master data
- **pfo_fund_infr_ht**: Source portfolio fund information history
- **pfo_stck_ma_t**: Target portfolio stock master (receives migrated data)
- **pfo_fund_infr_ht_t**: Target portfolio fund info history (receives migrated data)

Schema has fields for tracking: mncm_code (operator), proc_date, fund_code, itms_code (security code), plus financial metrics. All migration detail tables have execution_status, affected_rows, and error_message for audit trails.

### Core Modules

#### `modules/db_manager.py`
Database operations: init_db(), CRUD for migration jobs/details, query_table() with whitelist validation (prevents SQL injection on table names). Key functions return tuples of (success, message, affected_rows) or lists of dicts.

#### `modules/page_3/table_extractor.py`
LangChain/LanGraph workflow that calls LLM to extract table names from user SQL. Returns `branch_A_answer` (list of table names). This is called via `graph.invoke({"query": query})`.

#### `modules/page_3/sql_generator.py`
**`generate_sql_statements()`**: Takes extracted_tables + migration params (mncm_code, fund_code, itms_code, start_date, end_date) and returns list of dicts with:
- `table_name`: Original table
- `target_table`: f"{table}_t" (target table with _t suffix)
- `delete_sql`: WHERE-filtered DELETE
- `insert_sql`: WHERE-filtered INSERT FROM source

WHERE clause built from: mncm_code, proc_date BETWEEN [start_date, end_date], fund_code, and optional itms_code.

#### `modules/page_3/sql_executor.py`
**`execute_multiple_statements()`**: Takes SQL string (multiple statements separated by `;`), splits and executes each via sqlite3, commits, returns (success: bool, message: str, affected_rows: int).

### Pages

#### `pages/page_3.py` (Main migration page)
**Input Section (top)**:
- 5 columns: mncm_code, fund_code, itms_code, start_date, end_date
- Buttons: "추출하기" (Extract, primary), "작성하기" (Generate), "실행하기" (Execute All), "초기화" (Reset)

**Extraction Section**:
- Left: Query textarea (height 400)
- Right: Extracted tables dataframe

**SQL Display Section** (generated after "작성하기"):
- 4-column grid format with custom layout:
  - Col 1 (0.8 width): Checkbox for selection (st.checkbox, key: `sql_checkbox_{idx}`)
  - Col 2 (1 width): Table name text
  - Col 3 (3.2 width): Editable SQL textarea (height 150, key: `sql_textarea_{idx}`) with DELETE + INSERT
  - Col 4 (0.8 width): Execute button (key: `run_button_{idx}`) for single row execution

**Session State Management**:
- `result_df`: Dataframe of extracted tables
- `extracted_tables`: List of table names
- `sql_statements`: List of dicts (from sql_generator)
- `sql_edits`: Dict mapping idx → edited SQL text
- `sql_selections`: List of booleans for checkboxes
- `migration_params`: Input field values

**Key Logic**:
- extract_button: `graph.invoke()` → saves to result_df + extracted_tables → st.balloons() + st.toast() + st.rerun()
- generate_button: `generate_sql_statements()` → initializes sql_edits with defaults → initializes sql_selections as all True → st.toast() + st.rerun()
- Individual row "실행" button: Takes edited SQL from sql_edits[idx] → `execute_multiple_statements()` → st.success/error
- reset_button: Deletes result_df, extracted_tables, sql_statements, sql_edits, sql_selections → st.toast() + st.rerun()

**Dynamic List Sync**: sql_selections length is checked/adjusted every render:
```python
if 'sql_selections' not in st.session_state or len(st.session_state.sql_selections) != len(st.session_state.sql_statements):
    st.session_state.sql_selections = [True] * len(st.session_state.sql_statements)
```

#### `pages/page_4.py`
Table viewer with dropdown to select any allowed table, displays data via st.dataframe().

#### `pages/page_1.py`, `pages/page_2.py`
dbLink injection tools (not detailed in recent work).

## Important Implementation Details

1. **Toast vs. Success Messages**: Use `st.toast()` for notifications that should persist through st.rerun(). Inline `st.success()` disappears after rerun.

2. **Session State Initialization Pattern**:
   - On button click: Initialize missing keys with default values (e.g., sql_selections = [True] * len(...))
   - On every render: Check and sync array lengths if dependencies changed

3. **SQL Editing Workflow**:
   - sql_edits dict is keyed by index, not table name (matches sql_statements list order)
   - Default SQL built in text_area value parameter, then extracted from text_area input
   - Changes persist in session state across reruns

4. **Error Handling**: execute_multiple_statements() returns (False, error_msg, 0) on exception, so always check the boolean return value before using affected_rows.

5. **Database Paths**: DB_PATH computed via `os.path.dirname(__file__)` relative traversal (db_manager.py goes up 3 levels to repo root). Paths relative to module file, not cwd.

## Common Tasks

**Add a new field to migration inputs**: Add st.text_input/text_area in input section, add to migration_params dict, pass to generate_sql_statements(), update sql_generator.py where clause.

**Modify SQL generation logic**: Edit `modules/page_3/sql_generator.py:generate_sql_statements()`. Remember to return dicts with keys: table_name, target_table, delete_sql, insert_sql.

**Add table validation**: Extend migration_validation table usage in page_3.py or add new validation logic to sql_executor.py.

**Run single page for testing**: `streamlit run pages/page_3.py` (requires importing session state from modules, may have import errors).

## Notes for Future Work

- **Execute All Button**: The "실행하기" button is defined but not yet implemented. Should iterate sql_selections, execute all True entries, aggregate results.
- **LLM Integration**: table_extractor.py uses LangChain/LanGraph with GPT-5.4-nano (or similar model specified in env). Ensure API key (OPENAI_API_KEY or similar) is set in environment or .env file.
- **Database Initialization**: init_db() is called in main.py on startup. Tables created with IF NOT EXISTS, so safe to re-run.
- **SQL Injection Prevention**: Table names are validated via whitelist in db_manager.py:query_table(). Parameter placeholders used in db functions. Only user-entered column values in sql_generator.py WHERE clauses — assume trusted input within app (not exposed to external users).
