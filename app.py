from flask import Flask, jsonify, request, render_template_string
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

# --- HTML Template ---
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Repository</title>
</head>
<body>
    <h1>Student Repository</h1>
    <h2>All Students</h2>
    <ul>
        {% for student in students %}
            <li>
                ID: {{ student['id'] }} | Name: {{ student['name'] }} | Status: {{ student['status'] }}
                <form action="/student/{{ student['id'] }}/delete" method="post" style="display:inline;">
                    <button type="submit">Delete</button>
                </form>
                <form action="/student/{{ student['id'] }}/edit" method="post" style="display:inline;">
                    <input type="text" name="name" placeholder="New name">
                    <input type="text" name="status" placeholder="New status">
                    <button type="submit">Edit</button>
                </form>
            </li>
        {% endfor %}
    </ul>

    <h2>Add Student</h2>
    <form action="/student/add" method="post">
        <input type="text" name="name" placeholder="Name" required>
        <input type="text" name="status" placeholder="Status" required>
        <button type="submit">Add</button>
    </form>
</body>
</html>
"""

# --- Routes ---
@app.route('/students', methods=['GET'])
def show_students():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()
    students = [{"id": r[0], "name": r[1], "status": r[2]} for r in rows]
    return render_template_string(html_template, students=students)

@app.route('/student/add', methods=['POST'])
def add_student():
    name = request.form.get("name")
    status = request.form.get("status")
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, status) VALUES (?, ?)", (name, status))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Student '{name}' added successfully"}), 201

@app.route('/student/<int:student_id>/edit', methods=['POST'])
def edit_student(student_id):
    name = request.form.get("name")
    status = request.form.get("status")
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET name=?, status=? WHERE id=?", (name, status, student_id))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Student {student_id} updated successfully"})

@app.route('/student/<int:student_id>/delete', methods=['POST'])
def delete_student(student_id):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Student {student_id} deleted successfully"})

if __name__ == "__main__":
    app.run(debug=True)
