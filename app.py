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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
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
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f4f7f6;
            color: #333;
        }
        .dashboard-header {
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 20px 0;
            margin-bottom: 30px;
            border-radius: 0 0 20px 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .custom-card {
            background: white;
            border-radius: 12px;
            border: none;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        .custom-card:hover {
            transform: translateY(-5px);
        }
        .stat-icon {
            font-size: 2rem;
            opacity: 0.8;
        }
        .table-custom {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        .table-custom th {
            background-color: #f8f9fa;
            border-bottom: 2px solid #eaeaea;
            font-weight: 600;
        }
        .btn-custom-add {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px;
            font-weight: 600;
            transition: background 0.3s;
        }
        .btn-custom-add:hover {
            background-color: #2980b9;
        }
        .form-floating label {
            color: #7f8c8d;
        }
    </style>
</head>
<body>

    <div class="dashboard-header text-center">
        <h2><i class="fa-solid fa-graduation-cap me-2"></i> Student Information System</h2>
        <p class="mb-0 text-light">Manage records and track performance analytics</p>
    </div>

    <div class="container">
        <div class="row mb-4">
            <div class="col-md-3 col-sm-6 mb-3">
                <div class="card custom-card p-3 d-flex flex-row align-items-center justify-content-between">
                    <div>
                        <h6 class="text-muted mb-1">Total Students</h6>
                        <h3 class="mb-0" id="stat-total">0</h3>
                    </div>
                    <i class="fa-solid fa-users stat-icon text-primary"></i>
                </div>
            </div>
            <div class="col-md-3 col-sm-6 mb-3">
                <div class="card custom-card p-3 d-flex flex-row align-items-center justify-content-between">
                    <div>
                        <h6 class="text-muted mb-1">Class Average</h6>
                        <h3 class="mb-0" id="stat-avg">0</h3>
                    </div>
                    <i class="fa-solid fa-chart-line stat-icon text-info"></i>
                </div>
            </div>
            <div class="col-md-3 col-sm-6 mb-3">
                <div class="card custom-card p-3 d-flex flex-row align-items-center justify-content-between">
                    <div>
                        <h6 class="text-muted mb-1">Passed</h6>
                        <h3 class="mb-0 text-success" id="stat-passed">0</h3>
                    </div>
                    <i class="fa-solid fa-check-circle stat-icon text-success"></i>
                </div>
            </div>
            <div class="col-md-3 col-sm-6 mb-3">
                <div class="card custom-card p-3 d-flex flex-row align-items-center justify-content-between">
                    <div>
                        <h6 class="text-muted mb-1">Failed</h6>
                        <h3 class="mb-0 text-danger" id="stat-failed">0</h3>
                    </div>
                    <i class="fa-solid fa-times-circle stat-icon text-danger"></i>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-4 mb-4">
                <div class="card custom-card p-4">
                    <h5 class="mb-3"><i class="fa-solid fa-user-plus me-2"></i>New Record</h5>
                    <div id="alert-box"></div>
                    
                    <form id="student-form">
                        <div class="form-floating mb-3">
                            <input type="text" class="form-control" id="name" placeholder="John Doe" required>
                            <label for="name">Student Name</label>
                        </div>
                        <div class="form-floating mb-4">
                            <input type="number" class="form-control" id="grade" placeholder="85" step="0.1" required>
                            <label for="grade">Final Grade (0-100)</label>
                        </div>
                        <button type="submit" class="btn btn-custom-add w-100">
                            <i class="fa-solid fa-save me-1"></i> Save Student
                        </button>
                    </form>
                </div>
            </div>

            <div class="col-lg-8 mb-4">
                <div class="table-custom p-0">
                    <div class="p-3 border-bottom d-flex justify-content-between align-items-center bg-white">
                        <h5 class="mb-0"><i class="fa-solid fa-list me-2"></i>Enrolled Students</h5>
                        <button class="btn btn-sm btn-outline-secondary" onclick="fetchStudents(); fetchAnalytics();">
                            <i class="fa-solid fa-rotate-right"></i> Refresh
                        </button>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead>
                                <tr>
                                    <th class="ps-4">ID</th>
                                    <th>Name</th>
                                    <th>Grade</th>
                                    <th>Status</th>
                                    <th class="text-end pe-4">Action</th>
                                </tr>
                            </thead>
                            <tbody id="student-table-body">
                                </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", () => {
            fetchStudents();
            fetchAnalytics();
        });

        // Add Student
        document.getElementById("student-form").addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("name").value;
            const grade = document.getElementById("grade").value;
            const alertBox = document.getElementById("alert-box");

            const response = await fetch('/api/students', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, grade })
            });

            const result = await response.json();

            if (response.ok) {
                showAlert(result.message, 'success');
                document.getElementById("student-form").reset();
                fetchStudents();
                fetchAnalytics();
            } else {
                showAlert(result.error, 'danger');
            }
        });

        function showAlert(message, type) {
            const alertBox = document.getElementById("alert-box");
            alertBox.innerHTML = `<div class="alert alert-${type} py-2 small shadow-sm">${message}</div>`;
            setTimeout(() => alertBox.innerHTML = "", 3000);
        }

        // Fetch Students
        async function fetchStudents() {
            const response = await fetch('/api/students');
            const students = await response.json();
            const tbody = document.getElementById("student-table-body");
            
            if (students.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-4">No students found. Add one to get started!</td></tr>`;
                return;
            }

            tbody.innerHTML = "";
            students.forEach(student => {
                const badgeClass = student.remark === "Pass" ? "bg-success" : "bg-danger";
                tbody.innerHTML += `
                    <tr>
                        <td class="ps-4 text-muted">#${student.id}</td>
                        <td class="fw-semibold">${student.name}</td>
                        <td>${student.grade}</td>
                        <td><span class="badge ${badgeClass} px-2 py-1 rounded-pill">${student.remark}</span></td>
                        <td class="text-end pe-4">
                            <button class="btn btn-sm btn-outline-danger shadow-sm" onclick="deleteStudent(${student.id})">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });
        }

        // Delete Student
        async function deleteStudent(id) {
            if(confirm("Are you sure you want to delete this record?")) {
                await fetch(`/api/students/${id}`, { method: 'DELETE' });
                fetchStudents();
                fetchAnalytics();
            }
        }

        // Fetch Analytics
        async function fetchAnalytics() {
            const response = await fetch('/api/analytics');
            const stats = await response.json();
            document.getElementById("stat-total").innerText = stats.total;
            document.getElementById("stat-avg").innerText = stats.average;
            document.getElementById("stat-passed").innerText = stats.passed;
            document.getElementById("stat-failed").innerText = stats.failed;
        }
    </script>
</body>
</html>
"""

# ==========================================
# 3. ROUTES AND API
# ==========================================

# Serve the combined HTML
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# CREATE Student
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()
    if not data or 'name' not in data or 'grade' not in data:
        return jsonify({"error": "Missing name or grade field"}), 400
        
    name = data['name'].strip()
    if not name: return jsonify({"error": "Name cannot be empty"}), 400

    try: grade = float(data['grade'])
    except ValueError: return jsonify({"error": "Grade must be a number"}), 400
        
    if grade < 0 or grade > 100:
        return jsonify({"error": "Grade must be between 0 and 100"}), 400

    remark = get_remark(grade)

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, grade, remark) VALUES (?, ?, ?)", (name, grade, remark))
        conn.commit()
        return jsonify({"message": "Student added successfully!"}), 201

# READ All Students
@app.route('/api/students', methods=['GET'])
def get_students():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        students = [dict(row) for row in cursor.fetchall()]
        return jsonify(students), 200

# DELETE Student
@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (id,))
        conn.commit()
        return jsonify({"message": "Record deleted!"}), 200

# ANALYTICS Endpoint
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT grade FROM students")
        grades = [row[0] for row in cursor.fetchall()]
        
        total = len(grades)
        if total == 0:
            return jsonify({"total": 0, "average": 0, "passed": 0, "failed": 0}), 200
            
        avg_grade = sum(grades) / total
        passed = sum(1 for g in grades if g >= 75)
        
        return jsonify({
            "total": total,
            "average": round(avg_grade, 2),
            "passed": passed,
            "failed": total - passed
        }), 200

if __name__ == '__main__':
    init_db()
    # If running in VS Code locally, it will start here
    app.run(debug=True)
else:
    # Gunicorn uses this block when deployed to Render
    init_db()
