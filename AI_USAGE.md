# AI Usage Log

## AI Tools Used
- Antigravity (Google DeepMind Integrated Agent) powered by Gemini 3.1 Pro

## Key Prompts Used
- "Initialize a Flask application with SQLAlchemy models for Users, Expenses, ExpenseSplits, and Settlements."
- "Write a Python script using pandas to ingest a CSV and calculate shared expenses based on different split types: equal, unequal, percentage, and share."
- "Create a Jinja2 dashboard template to display user balances per currency and a list of recent expenses."

## Cases Where AI Produced Something Wrong

1. **Incorrect Date Parsing Logic:**
   - **What AI Did**: The AI initially wrote `dateutil.parser.parse(str(date_str), dayfirst=True)` for all dates. This correctly parsed "04/05/2026" as May 4th, but it incorrectly parsed standard ISO formats "2026-02-05" (Feb 5) as May 2, 2026. This caused the "Meera moved out after March 31" logic to trigger erroneously for February expenses.
   - **How I Caught It**: I wrote a test script `test_import.py` and noticed anomalies triggering on Row 4, 7, and 8, which were February expenses.
   - **What I Changed**: I modified the parser to explicitly check for `YYYY-MM-DD` using regex `re.match(r'^\d{4}-\d{2}-\d{2}$', ds)` and use `datetime.strptime` for it, falling back to `dateutil` for other formats.

2. **Skipping the Correct Conflicting Entry:**
   - **What AI Did**: For the Thalassa dinner conflict, the AI wrote logic: `if "hers is wrong" in notes.lower() ...: skip()`. This logic accidentally skipped Rohan's entry (which contained the note) instead of Aisha's entry (which was the incorrect one).
   - **How I Caught It**: I reviewed the output of the import report and realized it skipped Row 25 instead of Row 24.
   - **What I Changed**: I updated the condition to target Aisha's entry explicitly: `if "thalassa" in desc.lower() and amount == 2400 and payer and payer.name == "Aisha":`

3. **Jinja2 Template Syntax Error:**
   - **What AI Did**: The AI generated `{% end endfor %}` in the `index.html` template.
   - **How I Caught It**: Noticed the syntax error during code review before running the Flask application.
   - **What I Changed**: Used a file replacement to change `{% end endfor %}` to the correct `{% endfor %}` syntax.
