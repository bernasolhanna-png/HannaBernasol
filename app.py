from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB_FILE = 'students.db'

# ==========================================
# 1. DATABASE SETUP
# ==========================================
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Added 'section' column to the table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                section TEXT NOT NULL,
                grade REAL NOT NULL,
                remark TEXT NOT NULL
            )
        ''')
        conn.commit()

def get_remark(grade):
    return "Pass" if grade >= 75 else "Fail"

# ==========================================
# 2. ENHANCED HTML/CSS/JS TEMPLATE
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
        <p class="mb-0 text-light">Full CRUD: Create, Read, Update, Delete</p>
    </div>

    <div class="container">
        <div class="row mb-4">
            <div class="col-md-3 mb-3"><div class="card custom-card p-3 d-flex flex-row align-items-center justify-content-between"><div><h6 class="text-muted mb-1">Total</h6><h3 id="stat-total">0</h3></div><i class="fa-solid fa-users text-primary stat-icon"></i></div></div>
            <div class="col-md-3 mb-3"><div class="card custom-card p-3 d-flex flex-row align-items-center justify-content-between"><div><h6 class="text-muted mb-1">Average</h6><h3 id="stat-avg">0</h3></div><i class="fa-solid fa-chart-line text-info stat-icon"></i></div></div>
            <div class="col-md-3 mb-3"><div class="card custom-card p-3 d-flex flex-row align-items-center justify-content-between"><div><h6 class="text-muted mb-1">Passed</h6><h3 class="text-success" id="stat-passed">0</h3></div><i class="fa-solid fa-circle-check text-success stat-icon"></i></div></div>
            <div class="col-md-3 mb-3"><div class="card custom-card p-3 d-flex flex-row align-items-center justify-content-between"><div><h6 class="text-muted mb-1">Failed</h6><h3 class="text-danger" id="stat-failed">0</h3></div><i class="fa-solid fa-circle-xmark text-danger stat-icon"></i></div></div>
        </div>

        <div class="row">
            <div class="col-lg-4 mb-4">
                <div class="card custom-card p-4">
                    <h5 id="form-title" class="mb-3"><i class="fa-solid fa-user-plus me-2"></i>New Record</h5>
                    <div id="alert-box"></div>
                    <form id="student-form">
                        <input type="hidden" id="student-id">
                        <div class="form-floating mb-3">
                            <input type="text" class="form-control" id="name" placeholder="Name" required>
                            <label>Student Name</label>
                        </div>
                        <div class="form-floating mb-3">
                            <input type="text" class="form-control" id="section" placeholder="Section" required>
                            <label>Section</label>
                        </div>
                        <div class="form-floating mb-4">
                            <input type="number" class="form-control" id="grade" placeholder="85" step="0.1" required>
                            <label>Average Grade (0-100)</label>
                        </div>
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
                            <thead>
                                <tr>
                                    <th class="ps-4">Name</th>
                                    <th>Section</th>
                                    <th>Grade</th>
                                    <th>Status</th>
                                    <th class="text-end pe-4">Actions</th>
                                </tr>
                            </thead>
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
        const formTitle = document.getElementById("form-title");
        const cancelBtn = document.getElementById("cancel-edit");

        studentForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const id = document.getElementById("student-id").value;
            const payload = {
                name: document.getElementById("name").value,
                section: document.getElementById("section").value,
                grade: document.getElementById("grade").value
            };

            const url = id ? `/api/students/${id}` : '/api/students';
            const method = id ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                resetForm();
                fetchStudents();
                fetchAnalytics();
                showAlert(id ? "Record Updated!" : "Record Saved!", "success");
            } else {
                const err = await response.json();
                showAlert(err.error, "danger");
            }
        });

        async function fetchStudents() {
            const res = await fetch('/api/students');
            const data = await res.json();
            const tbody = document.getElementById("student-table-body");
            tbody.innerHTML = data.length ? "" : "<tr><td colspan='5' class='text-center py-4'>No records found</td></tr>";
            data.forEach(s => {
                tbody.innerHTML += `
                    <tr>
                        <td class="ps-4 fw-semibold">${s.name}</td>
                        <td>${s.section}</td>
                        <td>${s.grade}</td>
                        <td><span class="badge ${s.remark === 'Pass' ? 'bg-success' : 'bg-danger'}">${s.remark}</span></td>
                        <td class="text-end pe-4">
                            <button class="btn btn-sm btn-outline-primary me-1" onclick="editStudent(${s.id}, '${s.name}', '${s.section}', ${s.grade})"><i class="fa-solid fa-pen"></i></button>
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
            formTitle.innerHTML = '<i class="fa-solid fa-pen-to-square me-2"></i>Edit Record';
            submitBtn.innerText = "Update Student";
            cancelBtn.classList.remove("d-none");
        }

        function resetForm() {
            studentForm.reset();
            document.getElementById("student-id").value = "";
            formTitle.innerHTML = '<i class="fa-solid fa-user-plus me-2"></i>New Record';
            submitBtn.innerText = "Save Student";
            cancelBtn.classList.add("d-none");
        }

        async function deleteStudent(id) {
            if(confirm("Delete this record?")) {
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
# 3. ROUTES AND API
# ==========================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/students', methods=['GET'])
def get_students():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students ORDER BY id DESC")
        return jsonify([dict(row) for row in cursor.fetchall()])

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()
    name, section = data.get('name', '').strip(), data.get('section', '').strip()
    try:
        grade = float(data.get('grade', 0))
    except:
        return jsonify({"error": "Invalid grade"}), 400
    
    if not name or not section or grade < 0 or grade > 100:
        return jsonify({"error": "Invalid input data"}), 400

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, section, grade, remark) VALUES (?, ?, ?, ?)", 
                       (name, section, grade, get_remark(grade)))
        conn.commit()
    return jsonify({"message": "Success"}), 201

@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    name, section = data.get('name', '').strip(), data.get('section', '').strip()
    grade = float(data.get('grade', 0))
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET name=?, section=?, grade=?, remark=? WHERE id=?", 
                       (name, section, grade, get_remark(grade), id))
        conn.commit()
    return jsonify({"message": "Updated"})

@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id=?", (id,))
        conn.commit()
    return jsonify({"message": "Deleted"})

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT grade FROM students")
        grades = [row[0] for row in cursor.fetchall()]
        total = len(grades)
        if total == 0: return jsonify({"total": 0, "average": 0, "passed": 0, "failed": 0})
        passed = sum(1 for g in grades if g >= 75)
        return jsonify({"total": total, "average": round(sum(grades)/total, 2), "passed": passed, "failed": total - passed})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
else:
    init_db()
