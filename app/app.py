from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import Schema, fields, validates, validates_schema, ValidationError
from datetime import datetime
from app.models import db, User, Category, Record, Account

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)
migrate = Migrate(app, db)


# Schemas
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

    @validates('name')
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise ValidationError('Name must be at least 2 characters long')

class AccountSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    balance = fields.Float(dump_only=True)
    initial_balance = fields.Float(load_only=True, missing=0.0)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('initial_balance')
    def validate_initial_balance(self, value):
        if value < 0:
            raise ValidationError('Initial balance cannot be negative')

class DepositSchema(Schema):
    amount = fields.Float(required=True)

    @validates('amount')
    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError('Amount must be positive')

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

    @validates('name')
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise ValidationError('Name must be at least 2 characters long')

class RecordSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    category_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    date_time = fields.DateTime(dump_default=datetime.utcnow)

    @validates('amount')
    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError('Amount must be positive')

    @validates_schema
    def validate_associations(self, data, **kwargs):
        user = User.query.get(data['user_id'])
        if not user:
            raise ValidationError('User does not exist')
            
        category = Category.query.get(data['category_id'])
        if not category:
            raise ValidationError('Category does not exist')
            
        account = Account.query.filter_by(user_id=data['user_id']).first()
        if not account:
            raise ValidationError('User has no account')
            
        if account.balance < data['amount']:
            raise ValidationError('Insufficient funds')

# Initialize schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
record_schema = RecordSchema()
records_schema = RecordSchema(many=True)
deposit_schema = DepositSchema()

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

# Account endpoints
@app.route('/accounts', methods=['POST'])
def create_account():
    try:
        data = account_schema.load(request.json)
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        existing_account = Account.query.filter_by(user_id=data['user_id']).first()
        if existing_account:
            return jsonify({'error': 'User already has an account'}), 400
            
        account = Account(
            user_id=data['user_id'],
            initial_balance=data.get('initial_balance', 0.0)
        )
        db.session.add(account)
        db.session.commit()
        return account_schema.dump(account), 201
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/accounts/<int:id>', methods=['GET'])
def get_account(id):
    try:
        account = Account.query.get(id)
        if account is None:
            return jsonify({'error': 'Account not found'}), 404
        return account_schema.dump(account)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/accounts/<int:id>/deposit', methods=['POST'])
def deposit_to_account(id):
    try:
        data = deposit_schema.load(request.json)
        account = Account.query.get(id)
        if account is None:
            return jsonify({'error': 'Account not found'}), 404
            
        account.deposit(data['amount'])
        db.session.commit()
        return account_schema.dump(account)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    except ValueError as err:
        return jsonify({'error': str(err)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/accounts/<int:id>/balance', methods=['GET'])
def get_balance(id):
    try:
        account = Account.query.get(id)
        if account is None:
            return jsonify({'error': 'Account not found'}), 404
        return jsonify({'balance': account.balance})
    except Exception as e:
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
        record = Record.create_with_withdrawal(
            user_id=data['user_id'],
            category_id=data['category_id'],
            amount=data['amount']
        )
        return record_schema.dump(record), 201
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    except ValueError as err:
        return jsonify({'error': str(err)}), 400
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