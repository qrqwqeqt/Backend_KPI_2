from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, func

db = SQLAlchemy()

def get_smallest_available_id(model):
    """
    Find the smallest available ID for a given model.
    
    Args:
        model: SQLAlchemy model class
        
    Returns:
        int: Smallest available ID
    """
    # Get all existing IDs ordered
    stmt = select(model.id).order_by(model.id)
    existing_ids = [row[0] for row in db.session.execute(stmt)]
    
    if not existing_ids:
        return 1
        
    # Find first gap in sequence
    smallest_id = 1
    for current_id in existing_ids:
        if current_id != smallest_id:
            return smallest_id
        smallest_id += 1
        
    return smallest_id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    accounts = db.relationship('Account', backref='user', lazy=True, cascade="all, delete-orphan")
    records = db.relationship('Record', backref='user', lazy=True, cascade="all, delete-orphan")

    def __init__(self, name):
        self.name = name
        db.session.add(self)
        db.session.flush()  # Needed to get ID before commit
        self.id = get_smallest_available_id(User)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user_id, initial_balance=0.0):
        self.user_id = user_id
        self.balance = initial_balance
        db.session.add(self)
        db.session.flush()
        self.id = get_smallest_available_id(Account)

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount
        self.updated_at = datetime.utcnow()

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "balance": self.balance,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    records = db.relationship('Record', backref='category', lazy=True, cascade="all, delete-orphan")

    def __init__(self, name):
        self.name = name
        db.session.add(self)
        db.session.flush()
        self.id = get_smallest_available_id(Category)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, category_id, amount):
        self.user_id = user_id
        self.category_id = category_id
        self.amount = amount
        self.date_time = datetime.utcnow()
        db.session.add(self)
        db.session.flush()
        self.id = get_smallest_available_id(Record)

    @staticmethod
    def create_with_withdrawal(user_id, category_id, amount):
        """
        Creates a new record and withdraws the amount from the user's account
        """
        account = Account.query.filter_by(user_id=user_id).first()
        if not account:
            raise ValueError("User has no account")
        
        try:
            account.withdraw(amount)
            record = Record(user_id=user_id, category_id=category_id, amount=amount)
            db.session.commit()
            return record
        except Exception as e:
            db.session.rollback()
            raise e

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "amount": self.amount,
            "date_time": self.date_time
        }