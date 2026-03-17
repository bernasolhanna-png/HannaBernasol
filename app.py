from flask import Flask, request, redirect, render_template_string
import psycopg2
import psycopg2.extras
import json

app = Flask(__name__)

# SUPABASE CONNECTION STRING
DB_URL = "postgresql://postgres:Pusanitoji2005@db.msoslvbectkjqbfgmeei.supabase.co:5432/postgres"

def get_db():
    # Connect to your Supabase PostgreSQL database
    conn = psycopg2.connect(DB_URL)
    return conn

# HOME PAGE (READ & ANALYTICS)
@app.route('/')
def index():
    conn = get_db()
    # Using RealDictCursor so we can access columns by name like s['name'] in the template
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Get all students
    cur.execute("SELECT * FROM students ORDER BY id ASC")
    students = cur.fetchall()
    
    # --- DATA ANALYTICS LOGIC ---
    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) FROM students WHERE status='Passed'")
    passed = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) FROM students WHERE status='Failed'")
    failed = cur.fetchone()['count']
    
    cur.execute("SELECT AVG(gpa) FROM students")
    avg_gpa_row = cur.fetchone()['avg']
    avg_gpa = round(float(avg_gpa_row), 2) if avg_gpa_row else 0.0

    cur.execute("SELECT course, COUNT(*) FROM students GROUP BY course")
    course_data = cur.fetchall()
    courses = [row['course'] for row in course_data]
    course_counts = [row['count'] for row in course_data]
    
    cur.close()
    conn.close()

    # Note: I'm using the HTML you provided, but ensured variables match
    return render_template_string('''
    ''', students=students, total=total_students, passed=passed, failed=failed, 
       avg_gpa=avg_gpa, courses=courses, course_counts=course_counts)

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

        # Logic: GPA calculation (assuming lower is better based on your status check)
        gpa = (first_sem + second_sem) / 2
        status = "Passed" if gpa <= 3.0 else "Failed"

        conn = get_db()
        cur = conn.cursor()
        # PostgreSQL uses %s as placeholders
        cur.execute(
            "INSERT INTO students (student_id, name, course, year_level, first_sem, second_sem, gpa, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (student_id, name, course, year_level, first_sem, second_sem, gpa, status)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/')

    return render_template_string('''''')

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

        gpa = (first_sem + second_sem) / 2
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

    return render_template_string('''''', s=student)

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
