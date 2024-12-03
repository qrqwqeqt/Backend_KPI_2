from flask import Flask, jsonify, request

app = Flask(__name__)

users = {}
categories = {}
records = {}

def generate_id(data_store):
    return max(data_store.keys(), default=0) + 1

@app.route('/user/<int:user_id>', methods=['GET', 'DELETE'])
def user_by_id(user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404
    if request.method == 'GET':
        return jsonify(users[user_id])
    elif request.method == 'DELETE':
        del users[user_id]
        return jsonify({"message": "User deleted"})

@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    if not data.get("name"):
        return jsonify({"error": "Name is required"}), 400
    user_id = generate_id(users)
    users[user_id] = {"id": user_id, "name": data["name"]}
    return jsonify(users[user_id]), 201

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(list(users.values()))

@app.route('/category/<int:category_id>', methods=['DELETE'])
def category_by_id(category_id):
    if category_id not in categories:
        return jsonify({"error": "Category not found"}), 404
    del categories[category_id]
    return jsonify({"message": "Category deleted"})

@app.route('/category', methods=['GET', 'POST'])
def handle_categories():
    if request.method == 'GET':
        return jsonify(list(categories.values()))
    elif request.method == 'POST':
        data = request.json
        if not data.get("name"):
            return jsonify({"error": "Category name is required"}), 400
        category_id = generate_id(categories)
        categories[category_id] = {"id": category_id, "name": data["name"]}
        return jsonify(categories[category_id]), 201


@app.route('/record/<int:record_id>', methods=['GET', 'DELETE'])
def record_by_id(record_id):
    if record_id not in records:
        return jsonify({"error": "Record not found"}), 404
    if request.method == 'GET':
        return jsonify(records[record_id])
    elif request.method == 'DELETE':
        del records[record_id]
        return jsonify({"message": "Record deleted"})

@app.route('/record', methods=['POST', 'GET'])
def handle_records():
    if request.method == 'POST':
        data = request.json
        if not all([data.get("user_id"), data.get("category_id"), data.get("amount")]):
            return jsonify({"error": "All fields are required"}), 400
        record_id = generate_id(records)
        records[record_id] = {
            "id": record_id,
            "user_id": data["user_id"],
            "category_id": data["category_id"],
            "date_time": data.get("date_time"),
            "amount": data["amount"]
        }
        return jsonify(records[record_id]), 201
    elif request.method == 'GET':
        user_id = request.args.get("user_id", type=int)
        category_id = request.args.get("category_id", type=int)
        
        print(f"user_id={user_id}, category_id={category_id}")
        print("All records:", records)

        if not user_id and not category_id:
            return jsonify({"error": "Either user_id or category_id is required"}), 400
        
        filtered_records = [
            record for record in records.values()
            if (not user_id or record["user_id"] == user_id) and
               (not category_id or record["category_id"] == category_id)
        ]
        
        print("Filtered records:", filtered_records)
        
        return jsonify(filtered_records)



if __name__ == '__main__':
    app.run(debug=True)
