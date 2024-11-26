from flask import Flask, jsonify, request

app = Flask(__name__)

users = {}

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


if __name__ == '__main__':
    app.run(debug=True)
