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
    <h2>Student Information System</h2>

    <a href="/add">Add Student</a>

    <table border="1" cellpadding="5">
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

    {% for s in students %}
    <tr>
        <td>{{s.student_id}}</td>
        <td>{{s.name}}</td>
        <td>{{s.course}}</td>
        <td>{{s.year_level}}</td>
        <td>{{s.first_sem}}</td>
        <td>{{s.second_sem}}</td>
        <td>{{s.gpa}}</td>
        <td>{{s.status}}</td>
        <td>
            <a href="/edit/{{s.id}}">Edit</a>
            <a href="/delete/{{s.id}}">Delete</a>
        </td>
    </tr>
    {% endfor %}
    </table>
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
    <h2>Add Student</h2>

    <form method="post">

    Student ID<br>
    <input type="text" name="student_id"><br>

    Name<br>
    <input type="text" name="name"><br>

    Course<br>
    <input type="text" name="course"><br>

    Year Level<br>
    <input type="number" name="year_level"><br>

    1st Sem<br>
    <input type="number" step="0.01" name="first_sem"><br>

    2nd Sem<br>
    <input type="number" step="0.01" name="second_sem"><br><br>

    <button type="submit">Save</button>

    </form>

    <br>
    <a href="/">Back</a>
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
    <h2>Edit Student</h2>

    <form method="post">

    Student ID<br>
    <input type="text" name="student_id" value="{{s.student_id}}"><br>

    Name<br>
    <input type="text" name="name" value="{{s.name}}"><br>

    Course<br>
    <input type="text" name="course" value="{{s.course}}"><br>

    Year Level<br>
    <input type="number" name="year_level" value="{{s.year_level}}"><br>

    1st Sem<br>
    <input type="number" step="0.01" name="first_sem" value="{{s.first_sem}}"><br>

    2nd Sem<br>
    <input type="number" step="0.01" name="second_sem" value="{{s.second_sem}}"><br><br>

    <button type="submit">Update</button>

    </form>

    <br>
    <a href="/">Back</a>
    ''', s=student)


# DELETE STUDENT
@app.route('/delete/<int:id>')
def delete(id):

    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
