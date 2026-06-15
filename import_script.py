import pandas as pd
from datetime import datetime
import dateutil.parser
import re
from models import db, User, Expense, ExpenseSplit, Settlement
import math

def parse_date(date_str):
    try:
        if pd.isna(date_str) or not str(date_str).strip():
            return None
        ds = str(date_str).strip()
        # If format is YYYY-MM-DD
        if re.match(r'^\d{4}-\d{2}-\d{2}$', ds):
            return datetime.strptime(ds, "%Y-%m-%d").date()
        # Otherwise, assume DD/MM/YYYY or similar if possible
        return dateutil.parser.parse(ds, dayfirst=True).date()
    except:
        return None

def import_csv(file_path):
    anomalies = []
    df = pd.read_csv(file_path)

    # Initialize users from initial knowledge
    users = ["Aisha", "Rohan", "Priya", "Meera", "Dev", "Sam"]
    for u in users:
        if not User.query.filter_by(name=u).first():
            db.session.add(User(name=u))
    db.session.commit()

    def get_user(name):
        name = str(name).strip()
        if pd.isna(name) or not name: return None
        # Handle case insensitive matching and slight typos like "Priya S" or "rohan "
        for u in User.query.all():
            if u.name.lower() in name.lower() or name.lower() in u.name.lower():
                return u
        # Create temp user if not found (like Kabir)
        temp_user = User(name=name, is_active=False)
        db.session.add(temp_user)
        db.session.commit()
        anomalies.append(f"Notice: Created temporary inactive user for '{name}'.")
        return temp_user

    # Keep track of added expenses to detect duplicates
    added_expenses = []

    for index, row in df.iterrows():
        try:
            date_val = parse_date(row.get('date'))
            desc = str(row.get('description', '')).strip()
            paid_by_str = str(row.get('paid_by', '')).strip()
            amount_str = str(row.get('amount', '0'))
            amount_str = amount_str.replace(',', '')
            try:
                amount = float(amount_str)
            except:
                amount = 0.0
                
            currency = str(row.get('currency', 'INR')).strip()
            if pd.isna(currency) or currency == 'nan' or not currency:
                currency = 'INR'
                anomalies.append(f"Row {index+2}: Missing currency. Defaulting to INR.")

            split_type = str(row.get('split_type', '')).strip()
            if pd.isna(split_type) or split_type == 'nan': split_type = ''
            
            split_with = str(row.get('split_with', '')).strip()
            if pd.isna(split_with) or split_with == 'nan': split_with = ''
            
            split_details = str(row.get('split_details', '')).strip()
            if pd.isna(split_details) or split_details == 'nan': split_details = ''
            
            notes = str(row.get('notes', '')).strip()
            if pd.isna(notes) or notes == 'nan': notes = ''

            # Skip 0 amounts
            if amount == 0:
                anomalies.append(f"Row {index+2}: Amount is 0 ('{desc}'). Skipping.")
                continue

            payer = get_user(paid_by_str)

            # Anomaly: Settlement incorrectly logged
            if not split_type and ('settlement' in notes.lower() or 'paid back' in desc.lower()):
                anomalies.append(f"Row {index+2}: Identified as settlement. Amount: {amount}, Payer: {payer.name}")
                # Payee is in split_with usually
                payee_name = split_with
                payee = get_user(payee_name)
                if payer and payee:
                    s = Settlement(payer_id=payer.id, payee_id=payee.id, amount=amount, currency=currency, date=date_val)
                    db.session.add(s)
                continue
                
            # Anomaly: Duplicate Entries
            is_dup = False
            for ae in added_expenses:
                if ae['date'] == date_val and ae['amount'] == amount and ae['payer_id'] == (payer.id if payer else None):
                    # Check if desc is similar
                    is_dup = True
                    break
            
            if is_dup:
                anomalies.append(f"Row {index+2}: Duplicate entry detected ('{desc}'). Skipping.")
                continue

            # Anomaly: Explicit conflict rejection (Thalassa Aisha)
            if "thalassa" in desc.lower() and amount == 2400 and payer and payer.name == "Aisha":
                anomalies.append(f"Row {index+2}: Conflicting entry explicitly flagged ('{desc}'). Skipping.")
                continue

            # Check if negative (Refund)
            if amount < 0:
                anomalies.append(f"Row {index+2}: Negative amount detected ({amount}). Treating as refund.")
                amount = amount # Keep negative to deduct from balances
            
            expense = Expense(
                date=date_val,
                description=desc,
                paid_by_id=payer.id if payer else User.query.first().id,
                amount=amount,
                currency=currency,
                split_type=split_type,
                notes=notes
            )
            db.session.add(expense)
            db.session.flush() # get id
            
            added_expenses.append({
                'date': date_val,
                'amount': amount,
                'payer_id': expense.paid_by_id
            })

            # Users involved
            involved_users = []
            if split_with:
                names = [n.strip() for n in split_with.split(';')]
                for n in names:
                    if n:
                        u = get_user(n)
                        if u: involved_users.append(u)
            
            if not involved_users:
                continue

            # Anomaly: Someone moved out (Meera after March 31)
            active_users = []
            for u in involved_users:
                if u.name == "Meera" and date_val and date_val > datetime.strptime("2026-03-31", "%Y-%m-%d").date():
                    anomalies.append(f"Row {index+2}: Meera moved out but included in split. Removing her.")
                else:
                    active_users.append(u)
            
            if not active_users:
                continue

            # Calculate Splits
            if split_type == 'equal':
                if split_details:
                    anomalies.append(f"Row {index+2}: Split type is 'equal' but split_details are provided ('{split_details}'). Ignoring details and splitting equally.")
                split_amount = amount / len(active_users)
                for u in active_users:
                    s = ExpenseSplit(expense_id=expense.id, user_id=u.id, amount_owed=split_amount)
                    db.session.add(s)
            
            elif split_type == 'unequal':
                # Parse split details "Rohan 700; Priya 400; Meera 400"
                total_parsed = 0
                for part in split_details.split(';'):
                    part = part.strip()
                    if part:
                        parts = part.rsplit(' ', 1)
                        if len(parts) == 2:
                            u = get_user(parts[0])
                            val = float(parts[1])
                            total_parsed += val
                            if u in active_users:
                                s = ExpenseSplit(expense_id=expense.id, user_id=u.id, amount_owed=val)
                                db.session.add(s)
                
                # Check if total_parsed == amount? It might be different but we trust the split_details here.
                if total_parsed != amount:
                    anomalies.append(f"Row {index+2}: Unequal split total ({total_parsed}) != expense amount ({amount}). Trusting explicit splits.")

            elif split_type == 'percentage':
                # "Aisha 30%; Rohan 30%; Priya 30%; Meera 20%"
                percentages = {}
                total_pct = 0
                for part in split_details.split(';'):
                    part = part.strip()
                    if part:
                        parts = part.rsplit(' ', 1)
                        if len(parts) == 2:
                            u = get_user(parts[0])
                            val = float(parts[1].replace('%', ''))
                            if u in active_users:
                                percentages[u] = val
                                total_pct += val
                
                if total_pct != 100:
                    anomalies.append(f"Row {index+2}: Percentages sum to {total_pct}%. Normalizing to 100%.")
                
                for u, pct in percentages.items():
                    norm_pct = (pct / total_pct) if total_pct > 0 else 0
                    split_amount = amount * norm_pct
                    s = ExpenseSplit(expense_id=expense.id, user_id=u.id, amount_owed=split_amount)
                    db.session.add(s)
                    
            elif split_type == 'share':
                # "Aisha 2; Rohan 1; Priya 1"
                shares = {}
                total_shares = 0
                for part in split_details.split(';'):
                    part = part.strip()
                    if part:
                        parts = part.rsplit(' ', 1)
                        if len(parts) == 2:
                            u = get_user(parts[0])
                            val = float(parts[1])
                            if u in active_users:
                                shares[u] = val
                                total_shares += val
                
                for u, share in shares.items():
                    share_pct = (share / total_shares) if total_shares > 0 else 0
                    split_amount = amount * share_pct
                    s = ExpenseSplit(expense_id=expense.id, user_id=u.id, amount_owed=split_amount)
                    db.session.add(s)

        except Exception as e:
            anomalies.append(f"Row {index+2}: Error processing - {str(e)}")

    db.session.commit()
    return anomalies
