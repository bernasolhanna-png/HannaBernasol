from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
import os

app = Flask(__name__)

# --- DEPLOYMENT READY DATABASE CONFIG ---
db_url = os.environ.get('DATABASE_URL', 'sqlite:///quiz.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
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
    correct_option = db.Column(db.String(1), nullable=False)

class QuizScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)

# --- HTML TEMPLATES ---

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <title>Pro Quiz App</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #121212; font-family: 'Inter', sans-serif; color: #e0e0e0; }
        .navbar-custom { background: linear-gradient(135deg, #312e81, #1e3a8a); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4); }
        .card { background-color: #1e1e1e; border-radius: 16px; border: 1px solid #2d2d2d; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); margin-bottom: 1.5rem; transition: transform 0.2s; }
        .card:hover { transform: translateY(-2px); border-color: #404040; }
        
        /* Custom styled radio buttons for Dark Mode */
        .option-label {
            display: block; padding: 12px 20px; border: 2px solid #333; border-radius: 10px; background-color: #252525;
            cursor: pointer; transition: all 0.2s ease; font-weight: 500; color: #ccc;
        }
        .option-label:hover { border-color: #6366f1; background-color: #2a2a35; color: #fff; }
        .form-check-input { display: none; } /* Hide default radio */
        .form-check-input:checked + .option-label {
            border-color: #818cf8; background-color: rgba(99, 102, 241, 0.15); color: #818cf8;
            box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.3);
        }
        
        .btn-primary { background-color: #4f46e5; border: none; padding: 10px 20px; font-weight: 600; border-radius: 10px; color: #fff; }
        .btn-primary:hover { background-color: #6366f1; box-shadow: 0 0 10px rgba(99, 102, 241, 0.5); }
        .btn-success { background-color: #10b981; border: none; padding: 12px; font-weight: 600; border-radius: 10px; color: #000; }
        .btn-success:hover { background-color: #34d399; box-shadow: 0 0 10px rgba(16, 185, 129, 0.5); }
        
        .leaderboard-item { border-left: 4px solid transparent; transition: all 0.2s; background-color: transparent; border-bottom: 1px solid #333; }
        .leaderboard-item:hover { background-color: #252525; border-left-color: #818cf8; }
        .input-group-text, .form-control { background-color: #252525; border-color: #444; color: #fff; }
        .form-control:focus { background-color: #2a2a35; border-color: #6366f1; color: #fff; box-shadow: none; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark navbar-custom mb-5 py-3">
        <div class="container">
            <a class="navbar-brand fw-bold fs-4 text-white" href="/"><i class="fa-solid fa-brain me-2"></i>ProQuiz</a>
            <a href="/add" class="btn btn-outline-light btn-sm fw-bold shadow-sm"><i class="fa-solid fa-plus me-1"></i> Add Question</a>
        </div>
    </nav>
    <div class="container">
        {% if request.args.get('score') %}
        <div class="alert alert-success text-center fw-bold shadow-lg mb-4 rounded-3 fs-5 border-0" style="background-color: rgba(16, 185, 129, 0.2); color: #34d399;" role="alert">
            <i class="fa-solid fa-trophy me-2 text-warning"></i> Quiz Complete! You scored {{ request.args.get('score') }} points!
        </div>
        {% endif %}
        <div class="row g-4">
            <div class="col-lg-8">
                <form action="/submit_quiz" method="POST">
                    {% if questions %}
                        {% for q in questions %}
                        <div class="card p-4">
                            <h5 class="mb-4 fw-bold text-white"><i class="fa-regular fa-circle-question me-2" style="color: #818cf8;"></i>{{ loop.index }}. {{ q.text }}</h5>
                            <div class="row g-3">
                                {% for choice in [('A', q.option_a), ('B', q.option_b), ('C', q.option_c), ('D', q.option_d)] %}
                                <div class="col-md-6">
                                    <div class="form-check p-0">
                                        <input class="form-check-input" type="radio" name="q_{{ q.id }}" value="{{ choice[0] }}" id="q{{ q.id }}{{ choice[0] }}" required>
                                        <label class="option-label" for="q{{ q.id }}{{ choice[0] }}">
                                            <span class="badge me-2" style="background-color: #444; color: #fff;">{{ choice[0] }}</span> {{ choice[1] }}
                                        </label>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                        {% endfor %}
                        <div class="card p-4 mb-5">
                            <h5 class="fw-bold mb-3 text-white"><i class="fa-solid fa-user-pen me-2"></i>Save Your Score</h5>
                            <div class="input-group mb-4 shadow-sm rounded-3">
                                <span class="input-group-text border-end-0"><i class="fa-solid fa-user" style="color: #888;"></i></span>
                                <input type="text" name="username" class="form-control border-start-0 py-2" placeholder="Enter your name" required>
                            </div>
                            <button type="submit" class="btn btn-success w-100 fs-5"><i class="fa-solid fa-paper-plane me-2"></i>Submit Quiz</button>
                        </div>
                    {% else %}
                        <div class="text-center p-5 card rounded-4 shadow-sm">
                            <i class="fa-solid fa-folder-open fa-3x mb-3" style="color: #555;"></i>
                            <h4 class="text-white">No questions available</h4>
                            <p style="color: #aaa;">Be the first to add some questions to the database!</p>
                        </div>
                    {% endif %}
                </form>
            </div>
            
            <div class="col-lg-4">
                <div class="card p-0 overflow-hidden sticky-top shadow-lg" style="top: 20px;">
                    <div class="p-3 text-center" style="background-color: #1a1a24; border-bottom: 1px solid #333;">
                        <h5 class="fw-bold mb-0 text-white"><i class="fa-solid fa-ranking-star me-2 text-warning"></i>Leaderboard</h5>
                    </div>
                    <ul class="list-group list-group-flush bg-transparent">
                        {% for s in scores %}
                        <li class="list-group-item d-flex justify-content-between align-items-center p-3 leaderboard-item">
                            <span>
                                {% if loop.index == 1 %}<i class="fa-solid fa-medal text-warning me-2 fs-5"></i>
                                {% elif loop.index == 2 %}<i class="fa-solid fa-medal text-secondary me-2 fs-5"></i>
                                {% elif loop.index == 3 %}<i class="fa-solid fa-medal me-2 fs-5" style="color: #cd7f32;"></i>
                                {% else %}<span class="fw-bold me-3 ms-2" style="color: #666;">{{ loop.index }}</span>{% endif %}
                                <span class="fw-semibold text-light">{{ s.username }}</span>
                            </span>
                            <span class="badge rounded-pill" style="background-color: #4f46e5;">{{ s.score }} pts</span>
                        </li>
                        {% else %}
                        <li class="list-group-item text-center p-4 leaderboard-item" style="color: #888;">No scores yet. Play to be #1!</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

ADD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <title>Add Question - ProQuiz</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #121212; font-family: 'Inter', sans-serif; color: #e0e0e0; }
        .navbar-custom { background: linear-gradient(135deg, #312e81, #1e3a8a); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4); }
        .card { background-color: #1e1e1e; border-radius: 16px; border: 1px solid #2d2d2d; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); margin-bottom: 1.5rem; }
        .btn-primary { background-color: #4f46e5; border: none; padding: 10px 20px; font-weight: 600; border-radius: 10px; color: #fff; }
        .btn-primary:hover { background-color: #6366f1; box-shadow: 0 0 10px rgba(99, 102, 241, 0.5); }
        
        .input-group-text { background-color: #252525; border-color: #444; color: #818cf8; }
        .form-control, .form-select { background-color: #252525; border-color: #444; color: #fff; }
        .form-control:focus, .form-select:focus { background-color: #2a2a35; border-color: #6366f1; color: #fff; box-shadow: none; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark navbar-custom mb-5 py-3">
        <div class="container">
            <a class="navbar-brand fw-bold fs-4 text-white" href="/"><i class="fa-solid fa-brain me-2"></i>ProQuiz</a>
        </div>
    </nav>
    <div class="container mt-5">
        <div class="card p-5 mx-auto shadow-lg" style="max-width: 600px;">
            <div class="text-center mb-4">
                <i class="fa-solid fa-square-plus fa-3x mb-2" style="color: #818cf8;"></i>
                <h3 class="fw-bold text-white">Add New Question</h3>
                <p style="color: #aaa;">Expand the knowledge base!</p>
            </div>
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label fw-bold text-light"><i class="fa-solid fa-pen me-2"></i>Question Text</label>
                    <textarea name="text" class="form-control" rows="3" placeholder="What is the capital of..." required></textarea>
                </div>
                
                <div class="row g-2 mb-3">
                    <div class="col-md-6">
                        <div class="input-group">
                            <span class="input-group-text fw-bold">A</span>
                            <input type="text" name="option_a" class="form-control" placeholder="Option A" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="input-group">
                            <span class="input-group-text fw-bold">B</span>
                            <input type="text" name="option_b" class="form-control" placeholder="Option B" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="input-group">
                            <span class="input-group-text fw-bold">C</span>
                            <input type="text" name="option_c" class="form-control" placeholder="Option C" required>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="input-group">
                            <span class="input-group-text fw-bold">D</span>
                            <input type="text" name="option_d" class="form-control" placeholder="Option D" required>
                        </div>
                    </div>
                </div>

                <div class="mb-4">
                    <label class="form-label fw-bold text-light"><i class="fa-solid fa-check-circle me-2" style="color: #34d399;"></i>Correct Answer</label>
                    <select name="correct_option" class="form-select" required>
                        <option value="" disabled selected>Select the correct option...</option>
                        <option value="A">Option A</option>
                        <option value="B">Option B</option>
                        <option value="C">Option C</option>
                        <option value="D">Option D</option>
                    </select>
                </div>
                
                <button type="submit" class="btn btn-primary w-100 py-2 fs-5 mt-2"><i class="fa-solid fa-floppy-disk me-2"></i>Save Question</button>
                <div class="text-center mt-4">
                    <a href="/" class="text-decoration-none" style="color: #aaa;"><i class="fa-solid fa-arrow-left me-1"></i> Back to Quiz</a>
                </div>
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
    
    if score > 0 or any(k.startswith('q_') for k in request.form):
        db.session.add(QuizScore(username=username, score=score))
        db.session.commit()
        
    return redirect(url_for('index', score=score))

@app.route('/add', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        new_q = Question(
            text=request.form.get('text'), 
            option_a=request.form.get('option_a'),
            option_b=request.form.get('option_b'), 
            option_c=request.form.get('option_c'),
            option_d=request.form.get('option_d'), 
            correct_option=request.form.get('correct_option')
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
            ("What is the preferred Web Framework for this app?", "React", "Flask", "Laravel", "Spring", "B"),
            ("Which HTML tag is used for the largest heading?", "<h6>", "<header>", "<h1>", "<head>", "C")
        ]
        for s in seeds:
            db.session.add(Question(text=s[0], option_a=s[1], option_b=s[2], option_c=s[3], option_d=s[4], correct_option=s[5]))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
