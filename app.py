from flask import Flask, request, redirect, render_template_string
import psycopg2
import psycopg2.extras
import json

app = Flask(__name__)

# SUPABASE CONNECTION STRING
DB_URL = "postgresql://postgres:Pusanitoji2005@db.msoslvbectkjqbfgmeei.supabase.co:5432/postgres?sslmode=require
"

def get_db():
    conn = psycopg2.connect(DB_URL)
    return conn

# HOME PAGE (READ & ANALYTICS)
@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Get all students
        cur.execute("SELECT * FROM students ORDER BY id ASC")
        students = cur.fetchall()
        
        # --- DATA ANALYTICS LOGIC ---
        cur.execute("SELECT COUNT(*) FROM students")
        total_students = int(cur.fetchone()['count'])
        
        cur.execute("SELECT COUNT(*) FROM students WHERE status='Passed'")
        passed = int(cur.fetchone()['count'])
        
        cur.execute("SELECT COUNT(*) FROM students WHERE status='Failed'")
        failed = int(cur.fetchone()['count'])
        
        cur.execute("SELECT AVG(gpa) FROM students")
        avg_gpa_row = cur.fetchone()['avg']
        avg_gpa = round(float(avg_gpa_row), 2) if avg_gpa_row is not None else 0.0

        cur.execute("SELECT course, COUNT(*) FROM students GROUP BY course")
        course_data = cur.fetchall()
        courses = [row['course'] for row in course_data]
        course_counts = [int(row['count']) for row in course_data]
        
    finally:
        cur.close()
        conn.close()

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Student Information System</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style> body { background-color: #f8f9fa; } </style>
    </head>
    <body>
        <div class="container mt-5 mb-5">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="text-primary fw-bold"><i class="fas fa-user-graduate"></i> Student Information System</h2>
                <a href="/add" class="btn btn-success shadow-sm"><i class="fas fa-plus"></i> Add New Student</a>
            </div>
            
            <div class="card shadow-sm border-0 mb-4">
                <div class="card-header bg-dark text-white py-3">
                    <h5 class="mb-0"><i class="fas fa-chart-pie me-2"></i>Data Analytics Dashboard</h5>
                </div>
                <div class="card-body">
                    <div class="row text-center mb-4">
                        <div class="col-md-3">
                            <div class="p-3 bg-primary bg-opacity-10 rounded border border-primary text-primary">
                                <h6>Total Students</h6>
                                <h3 class="fw-bold mb-0">{{ total }}</h3>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="p-3 bg-success bg-opacity-10 rounded border border-success text-success">
                                <h6>Passed</h6>
                                <h3 class="fw-bold mb-0">{{ passed }}</h3>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="p-3 bg-danger bg-opacity-10 rounded border border-danger text-danger">
                                <h6>Failed</h6>
                                <h3 class="fw-bold mb-0">{{ failed }}</h3>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="p-3 bg-warning bg-opacity-10 rounded border border-warning text-dark">
                                <h6>Average GPA</h6>
                                <h3 class="fw-bold mb-0">{{ avg_gpa }}</h3>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-8">
                            <h6 class="text-center text-muted mb-3">Students per Course</h6>
                            <canvas id="courseChart" height="100"></canvas>
                        </div>
                        <div class="col-md-4">
                            <h6 class="text-center text-muted mb-3">Pass vs Fail Ratio</h6>
                            <canvas id="statusChart" height="200"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card shadow-sm border-0">
                <div class="card-header bg-white py-3 border-bottom">
                    <h5 class="mb-0 text-secondary"><i class="fas fa-list me-2"></i>Student Records</h5>
                </div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-hover table-striped mb-0 align-middle text-center">
                            <thead class="table-light">
                                <tr>
                                    <th>Student ID</th>
                                    <th>Name</th>
                                    <th>Course</th>
                                    <th>Year</th>
                                    <th>1st Sem</th>
                                    <th>2nd Sem</th>
                                    <th>GPA</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for s in students %}
                                <tr>
                                    <td class="fw-bold text-secondary">{{s.student_id}}</td>
                                    <td class="text-start">{{s.name}}</td>
                                    <td>{{s.course}}</td>
                                    <td>{{s.year_level}}</td>
                                    <td>{{s.first_sem}}</td>
                                    <td>{{s.second_sem}}</td>
                                    <td class="fw-bold">{{s.gpa}}</td>
                                    <td>
                                        {% if s.status == 'Passed' %}
                                            <span class="badge bg-success">Passed</span>
                                        {% else %}
                                            <span class="badge bg-danger">Failed</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        <a href="/edit/{{s.id}}" class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i></a>
                                        <a href="/delete/{{s.id}}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Are you sure you want to delete this record?');"><i class="fas fa-trash"></i></a>
                                    </td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="9" class="text-muted py-4">No students found. Click "Add New Student" to get started.</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const courses = {{ courses | tojson }};
            const courseCounts = {{ course_counts | tojson }};
            const passedCount = {{ passed }};
            const failedCount = {{ failed }};

            if (courses.length > 0) {
                const ctxCourse = document.getElementById('courseChart').getContext('2d');
                new Chart(ctxCourse, {
                    type: 'bar',
                    data: {
                        labels: courses,
                        datasets: [{
                            label: 'Number of Students',
                            data: courseCounts,
                            backgroundColor: '#0d6efd',
                            borderRadius: 4
                        }]
                    },
                    options: { 
                        responsive: true,
                        plugins: { legend: { display: false } },
                        scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
                    }
                });
            }

            const ctxStatus = document.getElementById('statusChart').getContext('2d');
            new Chart(ctxStatus, {
                type: 'doughnut',
                data: {
                    labels: ['Passed', 'Failed'],
                    datasets: [{
                        data: [passedCount, failedCount],
                        backgroundColor: ['#198754', '#dc3545']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        </script>
    </body>
    </html>
    ''', students=students, total=total_students, passed=passed, failed=failed, avg_gpa=avg_gpa, courses=courses, course_counts=course_counts)


# ADD STUDENT (CREATE)
@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        course = request.form['course']
        year_level = int(request.form['year_level'])
        first_sem = float(request.form['first_sem'])
        second_sem = float(request.form['second_sem'])

        gpa = round((first_sem + second_sem) / 2, 2)
        status = "Passed" if gpa <= 3.0 else "Failed"

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO students (student_id, name, course, year_level, first_sem, second_sem, gpa, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (student_id, name, course, year_level, first_sem, second_sem, gpa, status)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/')

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Student</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card shadow-sm border-0">
                        <div class="card-header bg-primary text-white py-3">
                            <h4 class="mb-0">Add New Student</h4>
                        </div>
                        <div class="card-body p-4">
                            <form method="post">
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">Student ID</label>
                                        <input type="text" class="form-control" name="student_id" required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">Full Name</label>
                                        <input type="text" class="form-control" name="name" required>
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-8">
                                        <label class="form-label fw-bold">Course</label>
                                        <input type="text" class="form-control" name="course" required>
                                    </div>
                                    <div class="col-md-4">
                                        <label class="form-label fw-bold">Year Level</label>
                                        <input type="number" class="form-control" name="year_level" min="1" max="5" required>
                                    </div>
                                </div>
                                <div class="row mb-4">
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">1st Sem Grade</label>
                                        <input type="number" step="0.01" class="form-control" name="first_sem" required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">2nd Sem Grade</label>
                                        <input type="number" step="0.01" class="form-control" name="second_sem" required>
                                    </div>
                                </div>
                                <div class="d-flex justify-content-end gap-2">
                                    <a href="/" class="btn btn-secondary px-4">Cancel</a>
                                    <button type="submit" class="btn btn-success px-4">Save Record</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')


# EDIT STUDENT (UPDATE)
@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        course = request.form['course']
        year_level = int(request.form['year_level'])
        first_sem = float(request.form['first_sem'])
        second_sem = float(request.form['second_sem'])

        gpa = round((first_sem + second_sem) / 2, 2)
        status = "Passed" if gpa <= 3.0 else "Failed"

        cur.execute(
            "UPDATE students SET student_id=%s, name=%s, course=%s, year_level=%s, first_sem=%s, second_sem=%s, gpa=%s, status=%s WHERE id=%s",
            (student_id, name, course, year_level, first_sem, second_sem, gpa, status, id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/')

    cur.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cur.fetchone()
    cur.close()
    conn.close()

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Edit Student</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card shadow-sm border-0">
                        <div class="card-header bg-primary text-white py-3">
                            <h4 class="mb-0">Edit Student Record</h4>
                        </div>
                        <div class="card-body p-4">
                            <form method="post">
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">Student ID</label>
                                        <input type="text" class="form-control" name="student_id" value="{{s.student_id}}" required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">Full Name</label>
                                        <input type="text" class="form-control" name="name" value="{{s.name}}" required>
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-8">
                                        <label class="form-label fw-bold">Course</label>
                                        <input type="text" class="form-control" name="course" value="{{s.course}}" required>
                                    </div>
                                    <div class="col-md-4">
                                        <label class="form-label fw-bold">Year Level</label>
                                        <input type="number" class="form-control" name="year_level" value="{{s.year_level}}" min="1" max="5" required>
                                    </div>
                                </div>
                                <div class="row mb-4">
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">1st Sem Grade</label>
                                        <input type="number" step="0.01" class="form-control" name="first_sem" value="{{s.first_sem}}" required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label fw-bold">2nd Sem Grade</label>
                                        <input type="number" step="0.01" class="form-control" name="second_sem" value="{{s.second_sem}}" required>
                                    </div>
                                </div>
                                <div class="d-flex justify-content-end gap-2">
                                    <a href="/" class="btn btn-secondary px-4">Cancel</a>
                                    <button type="submit" class="btn btn-primary px-4">Update Record</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    ''', s=student)

# DELETE STUDENT
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
