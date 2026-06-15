# Decision Log

This document records significant engineering and product decisions made during the development of the shared expenses app.

## 1. Technology Stack
- **Options Considered**: Node.js + Express, Next.js, Python + Flask, Django.
- **Decision**: Python + Flask with SQLite.
- **Why**: The primary complexity of this assignment lies in data parsing and anomaly handling rather than complex reactive UI. Python with `pandas` and `dateutil` offers superior data manipulation capabilities for CSV ingestion compared to Node.js. SQLite fulfills the relational DB requirement natively without the need to run a separate database server.

## 2. Multi-Currency Support
- **Options Considered**: 
  1. Convert all foreign currencies to a base currency (INR) using a hardcoded or dynamic exchange rate.
  2. Maintain independent ledgers for each currency.
- **Decision**: Maintain independent ledgers for each currency.
- **Why**: The user "Priya" explicitly complained that "The sheet pretends a dollar is a rupee. That can't be right." Converting at a fixed rate is often inaccurate for the time of the transaction. By maintaining separate currency balances, the app accurately reflects the exact amount owed in the exact currency used.

## 3. Handling Member Attrition (Moving In/Out)
- **Options Considered**: 
  1. Delete users when they leave.
  2. Use a `status` flag (`is_active`).
- **Decision**: `is_active` boolean flag.
- **Why**: Deleting users would break foreign key constraints on past expenses and invalidate historical calculations. Using `is_active` ensures data integrity while allowing the UI to exclude inactive members from future groups or login screens. 

## 4. Anomalies & Conflict Resolution (Thalassa Dinner)
- **Options Considered**: 
  1. Reject all duplicates blindly.
  2. Build a UI to ask the user which entry to keep.
  3. Resolve programmatically based on explicit keywords in notes.
- **Decision**: Resolve programmatically using notes and keywords.
- **Why**: The assignment required the importer to handle anomalies according to a documented policy. The notes provided explicit context ("hers is wrong"). Building a full interactive reconciliation UI was out of scope for a 2-day MVP, so a programmatic policy was the most robust choice.

## 5. Settlement Logic
- **Options Considered**: 
  1. Treat settlements as negative expenses.
  2. Treat them as a completely separate entity (`Settlement` table).
- **Decision**: Separate `Settlement` table.
- **Why**: Settlements do not involve a "split" among multiple people; they are a direct transfer between two specific users (Payer and Payee). Representing them in the `Expense` table requires hacky empty `split_type` logic. Moving them to a dedicated table makes balance calculation straightforward (`Amount Paid` - `Amount Owed` + `Settlements Received` - `Settlements Paid`).

## 6. CSS Framework
- **Options Considered**: TailwindCSS, Bootstrap, Vanilla CSS.
- **Decision**: Vanilla CSS.
- **Why**: To adhere strictly to the assignment's explicit guideline to prioritize Vanilla CSS and avoid build steps if unrequested, while keeping the application lightweight.
