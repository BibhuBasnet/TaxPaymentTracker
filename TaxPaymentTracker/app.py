from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DATABASE = 'tax_payment.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            amount REAL,
            payment_date TEXT,
            status TEXT,
            due_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return '''
        <h1>Welcome to the Tax Payment Tracker API!</h1>
        <div style="margin-top: 20px;">
            <a href="/payments" class="btn">Payments</a><br><br>
            <a href="/summary/June 15 2024" class="btn">Summary for June 15 2024</a><br><br>
            <a href="/summary/September 15 2024" class="btn">Summary for September 15 2024</a><br><br>
            <a href="/summary/January 15 2025" class="btn">Summary for January 15 2025</a>
        </div>
        
        <style>
            .btn {
                display: inline-block;
                padding: 10px 20px;
                margin-bottom: 10px;
                background-color: #007BFF;
                color: white;
                text-align: center;
                text-decoration: none;
                border-radius: 5px;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            
            .btn:hover {
                background-color: #0056b3;
            }
        </style>
    '''

@app.route('/payments', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_payments():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if request.method == 'POST':
        data = request.json
        c.execute('''
            INSERT INTO payments (company, amount, payment_date, status, due_date) 
            VALUES (?, ?, ?, ?, ?)
        ''', (data['company'], data['amount'], data['payment_date'], data['status'], data['due_date']))
        conn.commit()
        return jsonify({'message': 'Record added successfully'}), 201

    elif request.method == 'GET':
        c.execute('SELECT * FROM payments')
        records = c.fetchall()
        structured_records = [
            {'id': record[0], 'company': record[1], 'amount': record[2], 'payment_date': record[3], 'status': record[4], 'due_date': record[5]}
            for record in records
        ]
        return jsonify(structured_records)

    elif request.method == 'PUT':
        data = request.json
        c.execute('''
            UPDATE payments
            SET company = ?, amount = ?, payment_date = ?, status = ?, due_date = ?
            WHERE id = ?
        ''', (data['company'], data['amount'], data['payment_date'], data['status'], data['due_date'], data['id']))
        conn.commit()
        if c.rowcount == 0:
            return jsonify({'error': 'Record not found'}), 404
        return jsonify({'message': 'Record updated successfully'})

    elif request.method == 'DELETE':
        data = request.json
        c.execute('DELETE FROM payments WHERE id = ?', (data['id'],))
        conn.commit()
        return jsonify({'message': 'Record deleted successfully'})

    conn.close()

@app.route('/summary/<due_date>', methods=['GET'])
def filter_by_due_date(due_date):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM payments WHERE due_date = ?', (due_date,))
    records = c.fetchall()
    total_amount = sum(record[2] for record in records)
    tax_rate = 0.06  # 6% tax rate
    total_tax_due = total_amount * tax_rate
    structured_records = [
        {'id': record[0], 'company': record[1], 'amount': record[2], 'payment_date': record[3], 'status': record[4], 'due_date': record[5]}
        for record in records
    ]
    return jsonify({
        'records': structured_records,
        'total_amount': total_amount,
        'tax_rate': tax_rate * 100,
        'total_tax_due': total_tax_due,
    })

if __name__ == '__main__':
    app.run(debug=True)
