from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Routes ---
@app.route('/')
def home():
    return "Welcome to my Flask API with a repository database!"

# Get all students
@app.route('/students', methods=['GET'])
def get_students():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()
    students = [{"id": r[0], "name": r[1], "status": r[2]} for r in rows]
    return jsonify(students)

# Get one student by ID
@app.route('/student/<int:student_id>', methods=['GET'])
def get_student(student_id):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({"id": row[0], "name": row[1], "status": row[2]})
    return jsonify({"error": "Student not found"}), 404

# Add a new student
@app.route('/student', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data.get("name")
    status = data.get("status", "active")
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, status) VALUES (?, ?)", (name, status))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student added successfully"}), 201

# Update an existing student
@app.route('/student/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    name = data.get("name")
    status = data.get("status")
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET name=?, status=? WHERE id=?", (name, status, student_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student updated successfully"})

# Delete a student
@app.route('/student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student deleted successfully"})

if __name__ == "__main__":
    app.run(debug=True)
