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
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Random Quiz</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: sans-serif; }
        .card { border-radius: 12px; border: none; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-primary mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">🎯 Quiz App</a>
            <a href="/add" class="btn btn-outline-light btn-sm">+ Add Question</a>
        </div>
    </nav>
    <div class="container">
        {% if request.args.get('score') %}
        <div class="alert alert-success text-center fw-bold">You scored {{ request.args.get('score') }} points!</div>
        {% endif %}
        <div class="row">
            <div class="col-md-8">
                <form action="/submit_quiz" method="POST">
                    {% for q in questions %}
                    <div class="card mb-3 p-3">
                        <h5>{{ loop.index }}. {{ q.text }}</h5>
                        {% for choice in [('A', q.option_a), ('B', q.option_b), ('C', q.option_c), ('D', q.option_d)] %}
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="q_{{ q.id }}" value="{{ choice[0] }}" id="q{{ q.id }}{{ choice[0] }}" required>
                            <label class="form-check-label" for="q{{ q.id }}{{ choice[0] }}">{{ choice[0] }}) {{ choice[1] }}</label>
                        </div>
                        {% endfor %}
                    </div>
                    {% endfor %}
                    <div class="card p-3 mb-5">
                        <input type="text" name="username" class="form-control mb-2" placeholder="Your Name" required>
                        <button type="submit" class="btn btn-success w-100">Submit Quiz</button>
                    </div>
                </form>
            </div>
            <div class="col-md-4">
                <h4 class="fw-bold">🏆 Top 10 Scores</h4>
                <ul class="list-group">
                    {% for s in scores %}
                    <li class="list-group-item d-flex justify-content-between">
                        <span>{{ s.username }}</span> <b>{{ s.score }} pts</b>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
"""

ADD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><title>Add Question</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="card p-4 mx-auto" style="max-width: 600px;">
            <h3 class="mb-3">Add New Question</h3>
            <form method="POST">
                <textarea name="text" class="form-control mb-2" placeholder="Question Text" required></textarea>
                <input type="text" name="option_a" class="form-control mb-2" placeholder="Option A" required>
                <input type="text" name="option_b" class="form-control mb-2" placeholder="Option B" required>
                <input type="text" name="option_c" class="form-control mb-2" placeholder="Option C" required>
                <input type="text" name="option_d" class="form-control mb-2" placeholder="Option D" required>
                <select name="correct_option" class="form-select mb-3" required>
                    <option value="A">A is correct</option><option value="B">B is correct</option>
                    <option value="C">C is correct</option><option value="D">D is correct</option>
                </select>
                <button type="submit" class="btn btn-primary w-100">Save Question</button>
                <a href="/" class="btn btn-link w-100 mt-2">Back to Quiz</a>
            </form>
        </div>
    </div>
</body>
</html>
"""

# --- ROUTES ---
@app.route('/')
def index():
    random_questions = Question.query.order_by(func.random()).limit(10).all()
    top_scores = QuizScore.query.order_by(QuizScore.score.desc()).limit(10).all()
    return render_template_string(INDEX_TEMPLATE, questions=random_questions, scores=top_scores)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    username = request.form.get('username', 'Anonymous')
    score = 0
    for key, value in request.form.items():
        if key.startswith('q_'):
            q_id = int(key.split('_')[1])
            q = Question.query.get(q_id)
            if q and q.correct_option == value:
                score += 10
    db.session.add(QuizScore(username=username, score=score))
    db.session.commit()
    return redirect(url_for('index', score=score))

@app.route('/add', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        new_q = Question(
            text=request.form.get('text'), option_a=request.form.get('option_a'),
            option_b=request.form.get('option_b'), option_c=request.form.get('option_c'),
            option_d=request.form.get('option_d'), correct_option=request.form.get('correct_option')
        )
        db.session.add(new_q)
        db.session.commit()
        return redirect(url_for('add_question'))
    return render_template_string(ADD_TEMPLATE)

# --- INIT ---
with app.app_context():
    db.create_all()
    if not Question.query.first():
        seeds = [
            ("What is 5+5?", "10", "12", "15", "20", "A"),
            ("Python is a...", "Fruit", "Programming Language", "Car", "Movie", "B"),
            ("Web Framework for Python?", "React", "Flask", "Laravel", "Spring", "B")
        ]
        for s in seeds:
            db.session.add(Question(text=s[0], option_a=s[1], option_b=s[2], option_c=s[3], option_d=s[4], correct_option=s[5]))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
