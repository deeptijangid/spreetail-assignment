from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from models import db, User, Expense, ExpenseSplit, Settlement
from import_script import import_csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'spreetail_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    # Populate initial users if empty
    if not User.query.first():
        users = ["Aisha", "Rohan", "Priya", "Meera", "Dev", "Sam"]
        for u in users:
            db.session.add(User(name=u))
        db.session.commit()

@app.route('/')
def index():
    users = User.query.filter_by(is_active=True).all()
    return render_template('index.html', users=users)

@app.route('/login', methods=['POST'])
def login():
    user_id = request.form.get('user_id')
    if user_id:
        session['user_id'] = user_id
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    current_user = User.query.get(session['user_id'])
    users = User.query.filter_by(is_active=True).all()
    
    # Calculate balances
    # Balance = Amount paid by user - Amount owed by user
    # Do this per currency
    balances = {} # {currency: {user: balance}}
    
    # Initialize for active users
    for u in users:
        for cur in ['INR', 'USD']:
            if cur not in balances: balances[cur] = {}
            balances[cur][u.name] = 0.0

    # Amounts paid
    expenses = Expense.query.all()
    for e in expenses:
        if e.currency not in balances: balances[e.currency] = {}
        if e.paid_by.name not in balances[e.currency]: balances[e.currency][e.paid_by.name] = 0.0
        balances[e.currency][e.paid_by.name] += e.amount

    # Amounts owed
    splits = ExpenseSplit.query.all()
    for s in splits:
        cur = s.expense.currency
        if cur not in balances: balances[cur] = {}
        if s.user.name not in balances[cur]: balances[cur][s.user.name] = 0.0
        balances[cur][s.user.name] -= s.amount_owed

    # Settlements
    settlements = Settlement.query.all()
    for s in settlements:
        cur = s.currency
        if cur not in balances: balances[cur] = {}
        if s.payer.name not in balances[cur]: balances[cur][s.payer.name] = 0.0
        if s.payee.name not in balances[cur]: balances[cur][s.payee.name] = 0.0
        
        balances[cur][s.payer.name] += s.amount # Payer's balance goes up
        balances[cur][s.payee.name] -= s.amount # Payee's balance goes down

    return render_template('dashboard.html', current_user=current_user, balances=balances, users=users, expenses=expenses)

@app.route('/import', methods=['POST'])
def import_data():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('dashboard'))
    
    if file:
        filepath = os.path.join(app.root_path, 'uploads', file.filename)
        os.makedirs(os.path.join(app.root_path, 'uploads'), exist_ok=True)
        file.save(filepath)
        
        # Clear existing data for fresh import
        ExpenseSplit.query.delete()
        Expense.query.delete()
        Settlement.query.delete()
        User.query.filter_by(is_active=False).delete() # Remove temp users
        db.session.commit()
        
        anomalies = import_csv(filepath)
        return render_template('import_report.html', anomalies=anomalies)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
