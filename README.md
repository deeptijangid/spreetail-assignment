# Shared Expenses App (Splitwise Clone)

This is a full-stack web application designed to track shared expenses among flatmates, handle complex split logic, and reconcile debts. It natively parses messy CSV exports and resolves data anomalies based on defined policies.

## Features
- **Login**: Select an active user to view personalized balances.
- **Dynamic Group Membership**: Handles members joining and leaving.
- **Multiple Currencies**: Balances are maintained separately for USD and INR.
- **Complex Splits**: Supports Equal, Unequal, Percentage, and Share splits.
- **Anomaly Detection**: Seamlessly handles duplicates, refunds, bad math, and explicitly flagged conflicts during data import.

## Tech Stack
- **Backend**: Python 3.13, Flask, SQLAlchemy
- **Database**: SQLite (Relational DB)
- **Frontend**: HTML5, Vanilla CSS, Jinja2 Templates

## Setup Instructions

### Prerequisites
- Python 3.x installed.
- Pip package manager.

### Local Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Spreetail
   ```
2. Install the required Python dependencies:
   ```bash
   pip install flask flask-sqlalchemy pandas python-dateutil werkzeug
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Access the app:
   Open your browser and navigate to `http://localhost:5000`.

### Using the App
1. You will be greeted with the Login screen. Select a user (e.g., Aisha) and click "Log In".
2. You will see the dashboard with balances. Initially, it will be empty.
3. Use the **Import CSV** section to upload the `expenses_export.csv` file.
4. After importing, you will see an **Import Report** detailing all 13 anomalies that were detected and handled.
5. Click "Return to Dashboard" to view the calculated balances and expense history.

## Documentation
Please review the following documents included in the repository for detailed architectural context:
- `AI_CONTEXT.md`: Full project context, scope, and trade-offs.
- `SCOPE.md`: Database schema and comprehensive Anomaly Log.
- `DECISIONS.md`: Engineering and product decision log.
- `AI_USAGE.md`: Details of AI tool collaboration, prompts, and corrections.

## AI Used
- **Agent**: Gemini 3.1 Pro (High)
- See `AI_USAGE.md` for more details on prompt strategies and auto-corrections.

## Deployment
For this assignment, the app can be run locally using the provided instructions, which fulfills the required functionality. To deploy publicly, the SQLite database and Flask app can be easily pushed to services like PythonAnywhere or Render.
