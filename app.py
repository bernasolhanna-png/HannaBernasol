from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to my Flask API!"

@app.route('/api/data', methods=['GET'])
def get_data():
    # Example endpoint returning JSON
    sample_data = {"message": "Hello from the API!"}
    return jsonify(sample_data)

@app.route('/api/echo', methods=['POST'])
def echo():
    # Echo back JSON data sent in request
    data = request.get_json()
    return jsonify({"you_sent": data})

if __name__ == "__main__":
    # Run locally with Flask’s built-in server
    app.run(debug=True)
