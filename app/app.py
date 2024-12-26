from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import Schema, fields, ValidationError
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# SQLAlchemy Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    records = db.relationship('Record', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.name}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    records = db.relationship('Record', backref='category', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Category {self.name}>'

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Record {self.id}>'

# Marshmallow Schemas
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class RecordSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    category_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    date_time = fields.DateTime(dump_default=datetime.utcnow)

# Initialize schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
record_schema = RecordSchema()
records_schema = RecordSchema(many=True)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(ValidationError)
def validation_error(error):
    return jsonify({'error': 'Validation error', 'messages': error.messages}), 400

@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({'error': str(error)}), 500

# User endpoints
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = user_schema.load(request.json)
        user = User(name=data['name'])
        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user), 201
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return users_schema.dump(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        user = User.query.get(id)
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        return user_schema.dump(user)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.get(id)
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User successfully deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Category endpoints
@app.route('/categories', methods=['POST'])
def create_category():
    try:
        data = category_schema.load(request.json)
        category = Category(name=data['name'])
        db.session.add(category)
        db.session.commit()
        return category_schema.dump(category), 201
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        return categories_schema.dump(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/categories/<int:id>', methods=['GET'])
def get_category(id):
    try:
        category = Category.query.get(id)
        if category is None:
            return jsonify({'error': 'Category not found'}), 404
        return category_schema.dump(category)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    try:
        category = Category.query.get(id)
        if category is None:
            return jsonify({'error': 'Category not found'}), 404
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category successfully deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Record endpoints
@app.route('/records', methods=['POST'])
def create_record():
    try:
        data = record_schema.load(request.json)
        
        # Проверяем существование user и category
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': f"User with id {data['user_id']} not found"}), 404
            
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'error': f"Category with id {data['category_id']} not found"}), 404
            
        record = Record(
            user_id=data['user_id'],
            category_id=data['category_id'],
            amount=data['amount'],
            date_time=datetime.utcnow()
        )
        db.session.add(record)
        db.session.commit()
        return record_schema.dump(record), 201
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/records', methods=['GET'])
def get_records():
    try:
        records = Record.query.all()
        return records_schema.dump(records)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/records/<int:id>', methods=['GET'])
def get_record(id):
    try:
        record = Record.query.get(id)
        if record is None:
            return jsonify({'error': 'Record not found'}), 404
        return record_schema.dump(record)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)