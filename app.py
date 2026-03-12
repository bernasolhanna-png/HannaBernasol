from flask import Flask, jsonify, request

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return "Welcome to my Flask API!"

# Example JSON endpoint
@app.route('/api/data', methods=['GET'])
def get_data():
    sample_data = {"message": "Hello from the API!"}
    return jsonify(sample_data)

# Echo back posted JSON
@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify({"you_sent": data})

# Single student endpoint
@app.route('/student', methods=['GET'])
def student():
    student_info = {"id": 1, "name": "Alice", "status": "active"}
    return jsonify(student_info)

# Multiple students endpoint
@app.route('/students', methods=['GET'])
def students():
    student_list = [
        {"id": 1, "name": "Alice", "status": "active"},
        {"id": 2, "name": "Bob", "status": "inactive"},
        {"id": 3, "name": "Charlie", "status": "active"}
    ]
    return jsonify(student_list)

if __name__ == "__main__":
    # Run locally with Flask’s built-in server
    app.run(debug=True)
