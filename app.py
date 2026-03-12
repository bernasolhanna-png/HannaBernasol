from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            dept TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Combined HTML & CSS Template ---
# This string contains the entire frontend layout and styling.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Employee Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; border-bottom: 2px solid #3498db; pb: 10px; }
        
        /* Form Section */
        .add-form { display: flex; gap: 10px; margin-bottom: 30px; background: #ecf0f1; padding: 15px; border-radius: 8px; }
        input { padding: 10px; border: 1px solid #ccc; border-radius: 5px; flex: 1; }
        
        /* Table Styles */
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background-color: #3498db; color: white; }
        tr:hover { background-color: #f1f4f6; }

        /* Buttons */
        .btn { padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; color: white; font-weight: bold; }
        .btn-add { background-color: #27ae60; }
        .btn-update { background-color: #f39c12; }
        .btn-delete { background-color: #e74c3c; }
        .btn:hover { opacity: 0.8; }

        .action-cell { display: flex; gap: 5px; }
    </style>
</head>
<body>

<div class="container">
    <h1>Staff Directory Dashboard</h1>

    <form class="add-form" action="/add" method="post">
        <input type="text" name="name" placeholder="Name" required>
        <input type="text" name="role" placeholder="Role" required>
        <input type="text" name="dept" placeholder="Dept" required>
        <button type="submit" class="btn btn-add">Add Employee</button>
    </form>

    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Role</th>
                <th>Dept</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for emp in employees %}
            <tr>
                <form action="/edit/{{ emp[0] }}" method="post">
                    <td><input type="text" name="name" value="{{ emp[1] }}" style="width: 90%;"></td>
                    <td><input type="text" name="role" value="{{ emp[2] }}" style="width: 90%;"></td>
                    <td><input type="text" name="dept" value="{{ emp[3] }}" style="width: 90%;"></td>
                    <td class="action-cell">
                        <button type="submit" class="btn btn-update">Update</button>
                </form>
                        <form action="/delete/{{ emp[0] }}" method="post" style="display:inline;">
                            <button type="submit" class="btn btn-delete" onclick="return confirm('Are you sure?')">Delete</button>
                        </form>
                    </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

</body>
</html>
"""

# --- CRUD Routes ---

@app.route('/')
def index():
    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, employees=employees)

@app.route('/add', methods=['POST'])
def add_employee():
    name, role, dept = request.form.get("name"), request.form.get("role"), request.form.get("dept")
    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employees (name, role, dept) VALUES (?, ?, ?)", (name, role, dept))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_employee(id):
    name, role, dept = request.form.get("name"), request.form.get("role"), request.form.get("dept")
    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE employees SET name=?, role=?, dept=? WHERE id=?", (name, role, dept, id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == "__main__":
    # Standard Render/Heroku port configuration
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
