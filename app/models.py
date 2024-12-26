from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_time = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('records', lazy=True))
    category = db.relationship('Category', backref=db.backref('records', lazy=True))

    def __init__(self, user_id, category_id, amount, date_time=None):
        self.user_id = user_id
        self.category_id = category_id
        self.amount = amount
        self.date_time = date_time

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "amount": self.amount,
            "date_time": self.date_time
        }
