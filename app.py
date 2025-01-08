# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 14:56:42 2025

@author: ShahrozRehman
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os  # Import for handling environment variables

# Flask app setup
app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///holiday_requests.db'
db = SQLAlchemy(app)

# Database Model
class HolidayRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default="Pending")  # Pending, Approved, Rejected

# Create the database
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit_request():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        reason = request.form['reason']
        try:
            new_request = HolidayRequest(
                employee_name=name,
                email=email,
                start_date=datetime.strptime(start_date, '%Y-%m-%d'),
                end_date=datetime.strptime(end_date, '%Y-%m-%d'),
                reason=reason
            )
            db.session.add(new_request)
            db.session.commit()
            flash('Holiday request submitted successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
            return redirect(url_for('submit_request'))
    return render_template('submit.html')

@app.route('/status', methods=['GET', 'POST'])
def check_status():
    if request.method == 'POST':
        email = request.form['email']
        requests = HolidayRequest.query.filter_by(email=email).all()
        return render_template('status.html', requests=requests)
    return render_template('status.html', requests=None)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'admin123':
            requests = HolidayRequest.query.all()
            return render_template('admin.html', requests=requests)
        else:
            flash('Invalid admin password!', 'danger')
    return render_template('admin.html', requests=None)

@app.route('/update/<int:id>', methods=['POST'])
def update_status(id):
    new_status = request.form['status']
    request_to_update = HolidayRequest.query.get_or_404(id)
    request_to_update.status = new_status
    db.session.commit()
    flash('Request status updated successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/delete/<int:id>')
def delete_request(id):
    request_to_delete = HolidayRequest.query.get_or_404(id)
    db.session.delete(request_to_delete)
    db.session.commit()
    flash('Request deleted successfully!', 'success')
    return redirect(url_for('admin'))

# Dynamic port handling for Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Render's PORT or fallback to 5000 for local testing
    app.run(host='0.0.0.0', port=port, debug=True)
