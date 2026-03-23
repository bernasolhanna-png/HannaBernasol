import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# This pulls the URL from Render's Environment Variables (set in Step 5 below)
# If not found, it uses the internal URL you provided as a fallback.
DB_URL = os.environ.get('DATABASE_URL', 'postgresql://sis_db_9onl_user:CO0dbWnbIBjxKjbw5wniAfFKtsVJ46AC@dpg-d708fcp5pdvs7392k3a0-a/sis_db_9onl')

# ==========================================
# 1. DATABASE SETUP (PostgreSQL Version)
# ==========================================
def get_db_connection():
    return psycopg2.connect(DB_URL)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Note: PostgreSQL uses SERIAL for auto-increment
    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            section TEXT NOT NULL,
            grade REAL NOT NULL,
            remark TEXT NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def get_remark(grade):
    return "Pass" if grade >= 75 else "Fail"

# ==========================================
# 2. HTML TEMPLATE (Same as your previous version)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern SIS Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f4f7f6; color: #333; }
        .dashboard-header { background: linear-gradient(135deg, #2c3e50, #3498db); color: white; padding: 20px 0; border-radius: 0 0 20px 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .custom-card { background: white; border-radius: 12px; border: none; box-shadow: 0 5px 15px rgba(0,0,0,0.05); transition: transform 0.2s; }
        .stat-icon { font-size: 2rem; opacity: 0.8; }
        .table-custom { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }
        .btn-custom-add { background-color: #3498db; color: white; border-radius: 8px; font-weight: 600; }
    </style>
</head>
<body>
    <div class="dashboard-header text-center">
        <h2><i class="fa-solid fa-graduation-cap me-2"></i> Student Information System</h2>
        <p class="mb-0 text-light">Full CRUD with Persistent PostgreSQL</p>
    </div>

    <div class="container">
        <div class="row mb-4 text-center">
            <div class="col-md-3 mb-3"><div class="card custom-card p-3"><h6 class="text-muted">Total</h6><h3 id="stat-total">0</h3></div></div>
            <div class="col-md-3 mb-3"><div class="card custom-card p-3"><h6 class="text-muted">Average</h6><h3 id="stat-avg">0</h3></div></div>
            <div class="col-md-3 mb-3"><div class="card custom-card p-3"><h6 class="text-muted">Passed</h6><h3 class="text-success" id="stat-passed">0</h3></div></div>
            <div class="col-md-3 mb-3"><div class="card custom-card p-3"><h6 class="text-muted">Failed</h6><h3 class="text-danger" id="stat-failed">0</h3></div></div>
        </div>

        <div class="row">
            <div class="col-lg-4 mb-4">
                <div class="card custom-card p-4">
                    <h5 id="form-title" class="mb-3">New Record</h5>
                    <div id="alert-box"></div>
                    <form id="student-form">
                        <input type="hidden" id="student-id">
                        <div class="form-floating mb-3"><input type="text" class="form-control" id="name" placeholder="Name" required><label>Student Name</label></div>
                        <div class="form-floating mb-3"><input type="text" class="form-control" id="section" placeholder="Section" required><label>Section</label></div>
                        <div class="form-floating mb-4"><input type="number" class="form-control" id="grade" placeholder="Grade" step="0.1" required><label>Grade</label></div>
                        <button type="submit" id="submit-btn" class="btn btn-custom-add w-100">Save Student</button>
                        <button type="button" id="cancel-edit" class="btn btn-light w-100 mt-2 d-none" onclick="resetForm()">Cancel Edit</button>
                    </form>
                </div>
            </div>
            <div class="col-lg-8 mb-4">
                <div class="table-custom">
                    <div class="p-3 border-bottom d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Enrolled Students</h5>
                        <button class="btn btn-sm btn-outline-secondary" onclick="fetchStudents(); fetchAnalytics();">Refresh</button>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead><tr><th class="ps-4">Name</th><th>Section</th><th>Grade</th><th>Status</th><th class="text-end pe-4">Actions</th></tr></thead>
                            <tbody id="student-table-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", () => { fetchStudents(); fetchAnalytics(); });

        const studentForm = document.getElementById("student-form");
        const submitBtn = document.getElementById("submit-btn");
        const cancelBtn = document.getElementById("cancel-edit");

        studentForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const id = document.getElementById("student-id").value;
            const payload = {
                name: document.getElementById("name").value,
                section: document.getElementById("section").value,
                grade: document.getElementById("grade").value
            };
            const method = id ? 'PUT' : 'POST';
            const url = id ? `/api/students/${id}` : '/api/students';

            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                resetForm(); fetchStudents(); fetchAnalytics();
                showAlert(id ? "Updated!" : "Saved!", "success");
            }
        });

        async function fetchStudents() {
            const res = await fetch('/api/students');
            const data = await res.json();
            const tbody = document.getElementById("student-table-body");
            tbody.innerHTML = "";
            data.forEach(s => {
                tbody.innerHTML += `
                    <tr>
                        <td class="ps-4 fw-semibold">${s.name}</td>
                        <td>${s.section}</td>
                        <td>${s.grade}</td>
                        <td><span class="badge ${s.remark === 'Pass' ? 'bg-success' : 'bg-danger'}">${s.remark}</span></td>
                        <td class="text-end pe-4">
                            <button class="btn btn-sm btn-outline-primary" onclick="editStudent(${s.id}, '${s.name}', '${s.section}', ${s.grade})"><i class="fa-solid fa-pen"></i></button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteStudent(${s.id})"><i class="fa-solid fa-trash"></i></button>
                        </td>
                    </tr>`;
            });
        }

        function editStudent(id, name, section, grade) {
            document.getElementById("student-id").value = id;
            document.getElementById("name").value = name;
            document.getElementById("section").value = section;
            document.getElementById("grade").value = grade;
            submitBtn.innerText = "Update Student";
            cancelBtn.classList.remove("d-none");
        }

        function resetForm() {
            studentForm.reset();
            document.getElementById("student-id").value = "";
            submitBtn.innerText = "Save Student";
            cancelBtn.classList.add("d-none");
        }

        async function deleteStudent(id) {
            if(confirm("Delete this?")) {
                await fetch(`/api/students/${id}`, { method: 'DELETE' });
                fetchStudents(); fetchAnalytics();
            }
        }

        async function fetchAnalytics() {
            const res = await fetch('/api/analytics');
            const s = await res.json();
            document.getElementById("stat-total").innerText = s.total;
            document.getElementById("stat-avg").innerText = s.average;
            document.getElementById("stat-passed").innerText = s.passed;
            document.getElementById("stat-failed").innerText = s.failed;
        }

        function showAlert(msg, type) {
            const box = document.getElementById("alert-box");
            box.innerHTML = `<div class="alert alert-${type} py-2 small">${msg}</div>`;
            setTimeout(() => box.innerHTML = "", 3000);
        }
    </script>
</body>
</html>
"""

# ==========================================
# 3. ROUTES AND API (PostgreSQL Version)
# ==========================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    # RealDictCursor allows returning rows as dictionaries
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM students ORDER BY id DESC")
    students = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(students)

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data.get('name', '').strip()
    section = data.get('section', '').strip()
    grade = float(data.get('grade', 0))
    remark = get_remark(grade)

    conn = get_db_connection()
    cur = conn.cursor()
    # PostgreSQL uses %s placeholders instead of ?
    cur.execute("INSERT INTO students (name, section, grade, remark) VALUES (%s, %s, %s, %s)", 
                (name, section, grade, remark))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Success"}), 201

@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    name = data.get('name', '').strip()
    section = data.get('section', '').strip()
    grade = float(data.get('grade', 0))
    remark = get_remark(grade)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE students SET name=%s, section=%s, grade=%s, remark=%s WHERE id=%s", 
                (name, section, grade, remark, id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Updated"})

@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Deleted"})

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT grade FROM students")
    grades = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    
    total = len(grades)
    if total == 0: return jsonify({"total": 0, "average": 0, "passed": 0, "failed": 0})
    passed = sum(1 for g in grades if g >= 75)
    return jsonify({"total": total, "average": round(sum(grades)/total, 2), "passed": passed, "failed": total - passed})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
else:
    init_db()
