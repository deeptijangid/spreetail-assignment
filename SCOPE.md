# Scope & Anomaly Log

## Database Schema
The app uses a relational database (SQLite) via SQLAlchemy.

1. **User**
   - `id` (Integer, PK)
   - `name` (String, Unique)
   - `is_active` (Boolean, default: True) - Handles members who join/leave. Temporary members (like Kabir) get `is_active=False`.
2. **Expense**
   - `id` (Integer, PK)
   - `date` (Date)
   - `description` (String)
   - `paid_by_id` (Integer, FK to User)
   - `amount` (Float)
   - `currency` (String)
   - `split_type` (String) - equal, unequal, percentage, share
   - `notes` (Text)
   - `is_settlement` (Boolean)
3. **ExpenseSplit**
   - `id` (Integer, PK)
   - `expense_id` (Integer, FK to Expense)
   - `user_id` (Integer, FK to User)
   - `amount_owed` (Float) - The exactly calculated numeric share for the user.
4. **Settlement**
   - `id` (Integer, PK)
   - `payer_id` (Integer, FK to User)
   - `payee_id` (Integer, FK to User)
   - `amount` (Float)
   - `currency` (String)
   - `date` (Date)

## Anomaly Log

Below is the list of deliberate data problems found in the CSV and how the app handles them during import:

1. **Mixed Date Formats (Row 16, 27, 34 etc.)**: 
   - *Problem*: Dates formatted as YYYY-MM-DD, DD/MM/YYYY, or even "Mar 14". Row 34 is "04/05/2026" and ambiguous.
   - *Action*: Implemented a smart date parser using `dateutil` and regex. YYYY-MM-DD is prioritized, and `dayfirst=True` is used for DD/MM/YYYY to treat "04/05" as May 4 in the Indian context.
2. **Duplicate Entry (Row 5 & 6)**: 
   - *Problem*: "Dinner at Marina Bites" and "dinner - marina bites" for the same amount, payer, and date.
   - *Action*: The importer keeps an internal list of added expenses. If date, amount, and payer match, the second entry is skipped entirely.
3. **Unequal Split Doesn't Match Amount? (Row 12)**: 
   - *Problem*: "Aisha birthday cake" costs 1500. Split details: "Rohan 700; Priya 400; Meera 400". Aisha not charged.
   - *Action*: The math matches exactly (700+400+400=1500). The app natively supports parsing "Name Amount" from `split_details`.
4. **Settlement Logged as Expense (Row 14)**: 
   - *Problem*: "Rohan paid Aisha back", amount 5000. `split_type` is empty, note says "this is a settlement not an expense??".
   - *Action*: Identified via empty `split_type` and keywords. It is inserted into the `Settlement` table rather than the `Expense` table, directly decreasing Rohan's owed balance to Aisha.
5. **Percentages Exceed 100% (Row 15, Row 32)**: 
   - *Problem*: Aisha 30%, Rohan 30%, Priya 30%, Meera 20%. Sum is 110%.
   - *Action*: The importer detects the sum > 100 and normalizes it. Everyone's share is proportionally reduced (e.g., 30/110) to make it sum to 100%.
6. **Multiple Currencies (Row 20, 21, 23)**: 
   - *Problem*: Expenses logged in USD instead of INR.
   - *Action*: The app tracks balances independently per currency. "Priya: Gets back 100 INR, Owes 10 USD".
7. **Temporary/External Members (Row 23)**: 
   - *Problem*: "Dev's friend Kabir" included in the split. He isn't a flatmate.
   - *Action*: The app dynamically creates "Kabir" as an inactive User (`is_active=False`) just to record the debt properly without cluttering the main dashboard users list.
8. **Conflicting Duplicate Entries (Row 24, 25)**: 
   - *Problem*: Two entries for Thalassa dinner. Aisha logged 2400. Rohan logged 2450 with note "Aisha also logged this I think hers is wrong".
   - *Action*: The app explicitly checks for "Thalassa" by Aisha for 2400 and skips it based on the flag, honoring Rohan's entry.
9. **Refund / Negative Amount (Row 26)**: 
   - *Problem*: "Parasailing refund", -30 USD.
   - *Action*: Treated as a valid expense with a negative amount. This correctly credits all participants with their share of the refund.
10. **Missing Currency (Row 28)**:
    - *Problem*: Groceries DMart has an empty currency column.
    - *Action*: Importer detects missing currency and defaults to INR.
11. **Zero Amount Expense (Row 31)**:
    - *Problem*: "Dinner order Swiggy" with amount 0. Note says "counted twice earlier - fixing later".
    - *Action*: The app skips processing any expense where amount equals 0.
12. **Member Moved Out But Still Included (Row 36)**:
    - *Problem*: Meera moved out at the end of March, but is included in an April equal split.
    - *Action*: The importer checks the date. If date > March 31 and user is Meera, she is removed from the `active_users` for that split, and the cost is redistributed equally among the remaining members.
13. **Equal Split with Share Details (Row 42)**:
    - *Problem*: `split_type` is equal, but `split_details` provides shares.
    - *Action*: Importer logs a warning but honors the `split_type='equal'` column, ignoring the share details.
