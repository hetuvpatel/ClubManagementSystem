from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///club.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    debt = db.Column(db.Float, default=0)
    payments = db.relationship('Payment', backref='member', lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register_member():
    name = request.form['name']
    email = request.form['email']
    new_member = Member(name=name, email=email)
    db.session.add(new_member)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/pay', methods=['POST'])
def make_payment():
    member_id = request.form['member_id']
    amount = float(request.form['amount'])
    member = Member.query.get(member_id)
    if not member:
        return 'Member not found', 404
    new_payment = Payment(amount=amount, member_id=member_id)
    db.session.add(new_payment)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/member-statement/<int:member_id>', methods=['GET'])
def member_statement(member_id):
    member = Member.query.get(member_id)
    if not member:
        return "Member not found", 404
    total_payments = db.session.query(db.func.sum(Payment.amount)).filter(Payment.member_id == member_id).scalar() or 0
    return render_template('member_statement.html', member=member, total_payments=total_payments)

@app.route('/club-finances', methods=['GET'])
def club_financial_statement():
    total_revenue = db.session.query(db.func.sum(Payment.amount)).scalar() or 0
    total_coach_payments = 1000  # Example value
    current_month_rent = 500     # Example value
    return render_template('financial_statement.html', total_revenue=total_revenue,
                           total_coach_payments=total_coach_payments,
                           current_month_rent=current_month_rent)

def setup_database(app):
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    setup_database(app)
    app.run(debug=True)
