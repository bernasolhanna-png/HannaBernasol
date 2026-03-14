from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False) # 'A', 'B', 'C', or 'D'

class QuizScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)

# --- HTML TEMPLATES ---

# 1. Main Quiz & Leaderboard Template
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Random Quiz Challenge</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .navbar-brand { font-weight: bold; letter-spacing: 1px; }
        .card { border: none; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;}
        .section-title { color: #2c3e50; font-weight: 700; border-bottom: 3px solid #3498db; display: inline-block; padding-bottom: 5px; margin-bottom: 20px; }
        .form-check-label { cursor: pointer; width: 100%; padding: 5px; }
        .form-check-input:checked + .form-check-label { font-weight: bold; color: #0d6efd; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="/">🎯 Random Quiz Challenge</a>
            <div class="ms-auto">
                <a href="/add" class="btn btn-light btn-sm text-primary fw-bold">+ Add Question</a>
            </div>
        </div>
    </nav>
    <div class="container mt-5">
        
        {% if request.args.get('score') %}
        <div class="alert alert-success text-center fw-bold fs-4 shadow-sm" role="alert">
            🎉 Quiz Submitted! You scored {{ request.args.get('score') }} points!
        </div>
        {% endif %}

        <div class="row g-4">
            <div class="col-md-8">
                <h3 class="section-title">Answer these 10 random questions</h3>
                
                <form action="/submit_quiz" method="POST">
                    {% for q in questions %}
                    <div class="card border-primary mb-4">
                        <div class="card-body">
                            <h5 class="card-title fw-bold mb-3">{{ loop.index }}. {{ q.text }}</h5>
                            
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="radio" name="q_{{ q.id }}" id="q{{ q.id }}a" value="A" required>
                                <label class="form-check-label" for="q{{ q.id }}a">A) {{ q.option_a }}</label>
                            </div>
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="radio" name="q_{{ q.id }}" id="q{{ q.id }}b" value="B">
                                <label class="form-check-label" for="q{{ q.id }}b">B) {{ q.option_b }}</label>
                            </div>
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="radio" name="q_{{ q.id }}" id="q{{ q.id }}c" value="C">
                                <label class="form-check-label" for="q{{ q.id }}c">C) {{ q.option_c }}</label>
                            </div>
                            <div class="form-check mb-2">
                                <input class="form-check-input" type="radio" name="q_{{ q.id }}" id="q{{ q.id }}d" value="D">
                                <label class="form-check-label" for="q{{ q.id }}d">D) {{ q.option_d }}</label>
                            </div>
                        </div>
                    </div>
                    {% else %}
                    <p class="text-muted">No questions available. Add some first!</p>
                    {% endfor %}

                    {% if questions %}
                    <div class="card border-success mt-4">
                        <div class="card-body bg-light rounded">
                            <h5 class="mb-3">Ready to submit?</h5>
                            <div class="mb-3">
                                <input type="text" name="username" class="form-control form-control-lg" placeholder="Enter your Name to save score" required>
                            </div>
                            <button type="submit" class="btn btn-success btn-lg w-100 fw-bold">Submit Quiz & See Score</button>
                        </div>
                    </div>
                    {% endif %}
                </form>
            </div>

            <div class="col-md-4">
                <h3 class="section-title">🏆 Top Scores</h3>
                <ul class="list-group shadow-sm">
                    {% for score in scores %}
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <span class="fw-bold">{{ score.username }}</span>
                        <span class="badge bg-success rounded-pill fs-6">{{ score.score }} pts</span>
                    </li>
                    {% else %}
                    <li class="list-group-item text-muted">No scores yet. Be the first!</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
"""

# 2. Add Question Template
ADD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add New Quiz Question</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); font-family: 'Segoe UI', Tahoma, sans-serif; min-height: 100vh; }
        .card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2 class="text-primary fw-bold">Add a New Question</h2>
                    <a href="/" class="btn btn-outline-secondary">← Back to Quiz</a>
                </div>

                {% if success %}
                <div class="alert alert-success">Question added successfully! Add another?</div>
                {% endif %}

                <div class="card p-4 border-primary">
                    <form action="/add" method="POST">
                        <div class="mb-3">
                            <label class="form-label fw-bold">Question Text</label>
                            <textarea name="text" class="form-control" rows="3" required></textarea>
                        </div>
                        
                        <div class="row mb-3">
                            <div class="col-md-6 mb-2">
                                <label class="form-label">Option A</label>
                                <input type="text" name="option_a" class="form-control" required>
                            </div>
                            <div class="col-md-6 mb-2">
                                <label class="form-label">Option B</label>
                                <input type="text" name="option_b" class="form-control" required>
                            </div>
                            <div class="col-md-6 mb-2">
                                <label class="form-label">Option C</label>
                                <input type="text" name="option_c" class="form-control" required>
                            </div>
                            <div class="col-md-6 mb-2">
                                <label class="form-label">Option D</label>
                                <input type="text" name="option_d" class="form-control" required>
                            </div>
                        </div>

                        <div class="mb-4">
                            <label class="form-label fw-bold text-success">Which option is correct?</label>
                            <select name="correct_option" class="form-select" required>
                                <option value="" disabled selected>Select the correct answer...</option>
                                <option value="A">Option A</option>
                                <option value="B">Option B</option>
                                <option value="C">Option C</option>
                                <option value="D">Option D</option>
                            </select>
                        </div>

                        <button type="submit" class="btn btn-primary w-100 fw-bold fs-5">Save Question to Database</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def index():
    # Fetch exactly 10 questions randomly from the database
    random_questions = Question.query.order_by(func.random()).limit(10).all()
    # Fetch top 10 highest scores
    top_scores = QuizScore.query.order_by(QuizScore.score.desc()).limit(10).all()
    
    return render_template_string(INDEX_TEMPLATE, questions=random_questions, scores=top_scores)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    username = request.form.get('username', 'Anonymous')
    score = 0
    points_per_question = 10 
    
    # Loop through all submitted form data
    for key, value in request.form.items():
        if key.startswith('q_'): # Identifies our question inputs (e.g., "q_5")
            question_id = int(key.split('_')[1])
            question = Question.query.get(question_id)
            
            # Check if the submitted option matches the database's correct option
            if question and question.correct_option == value:
                score += points_per_question
                
    # Save the final score to the database
    new_score = QuizScore(username=username, score=score)
    db.session.add(new_score)
    db.session.commit()
    
    # Redirect back home with a success message flag in the URL
    return redirect(url_for('index', score=score))

@app.route('/add', methods=['GET', 'POST'])
def add_question():
    success = False
    if request.method == 'POST':
        # Get data from the form
        text = request.form.get('text')
        opt_a = request.form.get('option_a')
        opt_b = request.form.get('option_b')
        opt_c = request.form.get('option_c')
        opt_d = request.form.get('option_d')
        correct = request.form.get('correct_option')

        # Add to database
        new_question = Question(
            text=text, option_a=opt_a, option_b=opt_b, 
            option_c=opt_c, option_d=opt_d, correct_option=correct
        )
        db.session.add(new_question)
        db.session.commit()
        success = True
        
    return render_template_string(ADD_TEMPLATE, success=success)

# --- INITIALIZATION & SEEDING ---
def setup_database():
    with app.app_context():
        db.create_all()
        
        # Seed the database with 10 starting questions so the app isn't empty on launch
        if not Question.query.first():
            sample_questions = [
                ("What does HTML stand for?", "Hyper Text Preprocessor", "Hyper Text Markup Language", "Hyper Text Multiple Language", "Hyper Tool Multi Language", "B"),
                ("Which programming language is known as the language of the web?", "Python", "C++", "JavaScript", "Java", "C"),
                ("What is 15 + 25?", "30", "40", "50", "35", "B"),
                ("What does CSS stand for?", "Colorful Style Sheets", "Creative Style Sheets", "Cascading Style Sheets", "Computer Style Sheets", "C"),
                ("Which of the following is a Python web framework?", "Laravel", "Spring", "Django", "React", "C"),
                ("What is the main database used in this app?", "MySQL", "PostgreSQL", "SQLite", "MongoDB", "C"),
                ("Which HTTP method is used to submit form data?", "GET", "POST", "PUT", "DELETE", "B"),
                ("What symbol is used for comments in Python?", "//", "/*", "
