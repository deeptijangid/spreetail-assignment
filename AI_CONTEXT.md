# AI Context

## Product Understanding
The app is a shared expense manager (similar to Splitwise) that allows users to track expenses and settle debts. A core requirement is handling a messy CSV export with various data anomalies, detecting them, and applying consistent rules to handle them.

## Product Scope
- **Login Module:** Simple user selection/login.
- **Groups:** Members can join and leave groups over time.
- **Expenses:** Support equal, unequal, percentage, and share splits. Track multi-currency.
- **Balances:** Calculate who owes whom, individual and group-wide.
- **Settlements:** Record payments between users.
- **Import:** Ingest `expenses_export.csv` seamlessly while detecting and handling anomalies, generating an import report.

## Engineering Requirements
- Tech Stack: Python, Flask, SQLite, HTML/CSS (Vanilla).
- Relational Database only (SQLite).
- Must detect and handle at least 12 anomalies from the CSV export.
- Document all handled anomalies.

## Implementation Decisions & Trade-offs
- Used Python and Flask for simplicity and speed of development. SQLite handles the relational DB requirement seamlessly without external setup.
- Vanilla CSS avoids build steps and aligns with the requirement.
- **Multi-currency:** To handle USD and INR correctly without pretending USD is INR, the app will track balances per currency independently.
- **Users leaving/joining:** Users have an active period (joined/left dates). If they are included in a split outside their active dates, their share is redistributed to active members.

## Database Schema
- **User**: id, name, joined_date, left_date
- **Expense**: id, date, description, paid_by_id, amount, currency, split_type, notes
- **ExpenseSplit**: id, expense_id, user_id, amount_owed
- **Settlement**: id, payer_id, payee_id, amount, currency, date

## Frontend Structure
- Simple templates using Jinja2.
- `index.html`: Login and group overview.
- `dashboard.html`: Expense list, balances, add expense, settlement.
- `import_report.html`: Displays anomaly log after import.

## Anomalies & Policies (Draft)
1. **Duplicate Entries:** Same date, amount, payer, users, similar description -> Ignore duplicate.
2. **Missing Currency:** Default to INR.
3. **Invalid Percentage:** If sums > 100%, normalize to 100%.
4. **Member left:** If someone who moved out is charged, re-distribute their share among active members.
5. **Conflicting entries (Thalassa):** Note says "Aisha also logged this I think hers is wrong". Drop Aisha's entry.
6. **Refunds (Negative Amounts):** Processed as a reverse expense (credited back).
7. **Settlements typed as expenses:** Identify via "paid back" or "settlement" in notes and empty split_type.
8. **Date formats:** Parse mixed formats (DD/MM/YYYY, YYYY-MM-DD, Month DD) standardizing to YYYY-MM-DD.
9. **Zero Amount:** Ignore entirely.
10. **Typo in Split:** "Aisha 1; Rohan 1; Priya 1; Sam 1" under equal split -> Validated as equal.
11. **Temporary Member:** Added dynamically for the specific expense but not as a core active group member for subsequent ones.
12. **Wrong math in unequal:** We trust the explicitly stated amounts in `split_details`.

## Deployment Plan
- Local deployment using Flask development server.
- Can be deployed to Heroku, PythonAnywhere, or Vercel (using serverless functions) with SQLite.

## Testing Plan
- Execute the CSV import and review the generated balances to ensure anomalies are handled without crashing.
