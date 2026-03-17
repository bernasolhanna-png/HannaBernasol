from flask import Flask, request, redirect, render_template_string

import sqlite3



app = Flask(__name__)



# DATABASE CONNECTION

def get_db():

    conn = sqlite3.connect("students.db")

    conn.row_factory = sqlite3.Row

    return conn



# CREATE TABLE IF NOT EXISTS

def create_table():

    conn = get_db()

    conn.execute('''

    CREATE TABLE IF NOT EXISTS students(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        student_id TEXT,

        name TEXT,

        course TEXT,

        year_level INTEGER,

        first_sem REAL,

        second_sem REAL,

        gpa REAL,

        status TEXT

    )

    ''')

    conn.commit()

    conn.close()



create_table()



# HOME PAGE (READ)

@app.route('/')

def index():

    conn = get_db()

    students = conn.execute("SELECT * FROM students").fetchall()

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

        <style> body { background-color: #f8f9fa; } </style>

    </head>

    <body>

        <div class="container mt-5">

            <div class="d-flex justify-content-between align-items-center mb-4">

                <h2 class="text-primary fw-bold"><i class="fas fa-user-graduate"></i> Student Information System</h2>

                <a href="/add" class="btn btn-success shadow-sm"><i class="fas fa-plus"></i> Add New Student</a>

            </div>

            

            <div class="card shadow-sm">

                <div class="card-body p-0">

                    <div class="table-responsive">

                        <table class="table table-hover table-striped mb-0 align-middle text-center">

                            <thead class="table-dark">

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

                                        <a href="/edit/{{s.id}}" class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i> Edit</a>

                                        <a href="/delete/{{s.id}}" class="btn btn-sm btn-outline-danger" onclick="return confirm('Are you sure you want to delete this record?');"><i class="fas fa-trash"></i> Delete</a>

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

    </body>

    </html>

    ''', students=students)





# ADD STUDENT (CREATE)

@app.route('/add', methods=['GET','POST'])

def add():

    if request.method == 'POST':

        student_id = request.form['student_id']

        name = request.form['name']

        course = request.form['course']

        year_level = request.form['year_level']

        first_sem = float(request.form['first_sem'])

        second_sem = float(request.form['second_sem'])



        gpa = (first_sem + second_sem) / 2

        status = "Passed" if gpa <= 3 else "Failed"



        conn = get_db()

        conn.execute(

            "INSERT INTO students (student_id,name,course,year_level,first_sem,second_sem,gpa,status) VALUES (?,?,?,?,?,?,?,?)",

            (student_id,name,course,year_level,first_sem,second_sem,gpa,status)

        )

        conn.commit()

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

    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()



    if request.method == 'POST':

        student_id = request.form['student_id']

        name = request.form['name']

        course = request.form['course']

        year_level = request.form['year_level']

        first_sem = float(request.form['first_sem'])

        second_sem = float(request.form['second_sem'])



        gpa = (first_sem + second_sem) / 2

        status = "Passed" if gpa <= 3 else "Failed"



        conn.execute(

            "UPDATE students SET student_id=?,name=?,course=?,year_level=?,first_sem=?,second_sem=?,gpa=?,status=? WHERE id=?",

            (student_id,name,course,year_level,first_sem,second_sem,gpa,status,id)

        )

        conn.commit()

        conn.close()



        return redirect('/')



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

                                        <label class="form-label 
