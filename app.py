from flask import Flask, render_template, request, redirect, url_for
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

# --- Routes ---

@app.route('/')
def index():
    conn = sqlite3.connect("employees.db")
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return render_template("index.html", employees=employees)

@app.route('/add', methods=['POST'])
def add_employee():
    name = request.form.get("name")
    role = request.form.get("role")
    dept = request.form.get("dept")
    
    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employees (name, role, dept) VALUES (?, ?, ?)", (name, role, dept))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_employee(id):
    name = request.form.get("name")
    role = request.form.get("role")
    dept = request.form.get("dept")
    
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
    # Render requires the host to be 0.0.0.0 and port from environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
