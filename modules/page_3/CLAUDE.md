# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the `page_3` module of a Streamlit-based SQL helper application (SQL 보조기). This module implements the **TABLE 추출기** (Table Extractor) feature that automatically extracts table names from SQL queries using LLM-powered workflows.

## Architecture

The `table_extractor.py` module implements a **parallel verification workflow** using LangGraph:

- **Dual-branch extraction**: The query is processed through two parallel branches (Branch A and Branch B) to extract tables independently
- **Verification node**: Compares results from both branches to ensure consistency
- **Re-execution on mismatch**: If the results differ, the workflow re-runs the extraction until both branches agree
- **LLM**: Uses OpenAI's GPT-5.4-nano model for fast, lightweight table extraction

### Key Components

1. **AgentState** (TypedDict): Defines the workflow state with fields:
   - `query`: The SQL query input
   - `branch_A_answer`: Table list from branch A
   - `branch_B_answer`: Table list from branch B
   - `verification`: Boolean indicating if branches match

2. **table_extract_node**: Extracts tables from the query using structured output (TableList/Table Pydantic models)

3. **verification_node**: Compares branch results

4. **graph**: The compiled LangGraph workflow that manages the orchestration

### How It's Used

The page_3.py page calls `graph.invoke({"query": query})` and receives a result dictionary containing the extracted table names. Results are displayed in a Streamlit DataFrame.

## Development Setup

### Prerequisites
- Python 3.8+
- Dependencies from `requirements.txt` (LangChain, LanGraph, Streamlit, OpenAI)
- OpenAI API key configured in Streamlit secrets

### Running the Application

From the project root (`/Users/junmo/Desktop/jun_mini/programming/toy_2`):

```bash
streamlit run main.py
```

This launches a multi-page app. Navigate to "table 추출기" to test the table extraction feature.

### Testing the Module Directly

To test the table extraction workflow in isolation:

```python
from modules.page_3.table_extractor import graph

result = graph.invoke({"query": "SELECT * FROM users u JOIN orders o ON u.id = o.user_id"})
print(result['branch_A_answer'])  # ['orders', 'users']
```

## Key Design Notes

1. **Parallel Verification Pattern**: The dual-branch approach with verification provides confidence in extraction accuracy for SQL parsing, which can be error-prone with LLMs. If results diverge, the workflow automatically retries until consistency is achieved.

2. **Dummy Start Node**: A workaround exists (`dummy_start_node`) because START doesn't support edge-based branching in LangGraph. This node bridges START to the parallel branches.

3. **Model Choice**: GPT-5.4-nano was chosen for cost/speed tradeoffs (noted in comments as a replacement for slower ReAct implementation).

4. **Structured Output**: Uses Pydantic models (TableList, Table) to ensure the LLM returns valid JSON-like output with proper schema.

5. **Streamlit Secrets**: API keys are retrieved via `st.secrets["OPENAI_API_KEY"]` rather than environment variables, which is Streamlit's recommended approach for web apps.

## Common Tasks

### Adding Validation or Post-Processing

If you need to validate extracted tables or apply custom logic (e.g., filtering certain table names):

1. Add a new node to the graph (e.g., `validation_node`)
2. Connect it after `verification_node` before the END state
3. Update the conditional edges accordingly

### Adjusting the LLM or Parallel Logic

- Change the model: Edit the `ChatOpenAI(model='...')` instantiation
- Modify extraction logic: Update the `table_extract_prompt` template in `table_extract_node`
- Reduce/increase branches: You can modify the branching structure, but ensure the verification logic stays consistent

### Debugging Workflow Issues

The workflow includes `print()` statements in `verification_node`. Enable Streamlit's log viewing or check terminal output when running `streamlit run main.py` to see debug output.

## Related Files

- **pages/page_3.py**: The Streamlit UI that calls this module
- **modules/page_1/ and modules/page_2/**: Similar modules for dbLink injection features
- **main.py**: Multi-page app navigation