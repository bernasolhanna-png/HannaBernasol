from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    votes_a = db.Column(db.Integer, default=0)
    votes_b = db.Column(db.Integer, default=0)

class QuizScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)

# --- HTML TEMPLATE STRING ---
# This replaces the need for a separate templates folder
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fun Learning Hub</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .navbar-brand { font-weight: bold; letter-spacing: 1px; }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        .card:hover { transform: translateY(-5px); }
        .section-title {
            color: #2c3e50;
            font-weight: 700;
            border-bottom: 3px solid #3498db;
            display: inline-block;
            padding-bottom: 5px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="/">🚀 Learning Hub</a>
        </div>
    </nav>
    <div class="container mt-5">
        <div class="row g-4">
            
            <div class="col-md-4">
                <h3 class="section-title">Mini Blog</h3>
                {% for post in posts %}
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title text-primary">{{ post.title }}</h5>
                        <p class="card-text text-muted">{{ post.content }}</p>
                        <a href="{{ url_for('like_post', post_id=post.id) }}" class="btn btn-sm btn-outline-danger">
                            ❤️ Like ({{ post.likes }})
                        </a>
                    </div>
                </div>
                {% else %}
                <p class="text-muted">No blog posts yet.</p>
                {% endfor %}
            </div>

            <div class="col-md-4">
                <h3 class="section-title">Live Polls</h3>
                {% for poll in polls %}
                <div class="card mb-3 border-info">
                    <div class="card-body">
                        <h6 class="card-title">{{ poll.question }}</h6>
                        <div class="d-grid gap-2 mt-3">
                            <a href="{{ url_for('vote_poll', poll_id=poll.id, option='a') }}" class="btn btn-outline-info">
                                {{ poll.option_a }} <span class="badge bg-info text-dark ms-2">{{ poll.votes_a }}</span>
                            </a>
                            <a href="{{ url_for('vote_poll', poll_id=poll.id, option='b') }}" class="btn btn-outline-secondary">
                                {{ poll.option_b }} <span class="badge bg-secondary ms-2">{{ poll.votes_b }}</span>
                            </a>
                        </div>
                    </div>
                </div>
                {% else %}
                <p class="text-muted">No active polls.</p>
                {% endfor %}
            </div>

            <div class="col-md-4">
                <h3 class="section-title">Quick Quiz</h3>
                <div class="card mb-4 border-success">
                    <div class="card-body">
                        <form action="/submit_quiz" method="POST">
                            <div class="mb-3">
                                <label class="form-label fw-bold">What is 2 + 2?</label>
                                <input type="number" name="q1" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <input type="text" name="username" class="form-control" placeholder="Your Name" required>
                            </div>
                            <button type="submit" class="btn btn-success w-100">Submit Answer</button>
                        </form>
                    </div>
                </div>

                <h4 class="text-secondary mt-4">Top Scores</h4>
                <ul class="list-group shadow-sm">
                    {% for score in scores %}
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        {{ score.username }}
                        <span class="badge bg-success rounded-pill">{{ score.score }} pts</span>
                    </li>
                    {% else %}
                    <li class="list-group-item text-muted">No scores yet.</li>
                    {% endfor %}
                </ul>
            </div>

        </div>
    </div>
</body>
</html>
"""

# --- ROUTES ---
@app.route('/')
def index():
    posts = BlogPost.query.order_by(BlogPost.id.desc()).all()
    polls = Poll.query.all()
    scores = QuizScore.query.order_by(QuizScore.score.desc()).limit(5).all()
    
    # Using render_template_string instead of render_template
    return render_template_string(HTML_TEMPLATE, posts=posts, polls=polls, scores=scores)

@app.route('/like/<int:post_id>')
def like_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/vote/<int:poll_id>/<string:option>')
def vote_poll(poll_id, option):
    poll = Poll.query.get_or_404(poll_id)
    if option == 'a':
        poll.votes_a += 1
    elif option == 'b':
        poll.votes_b += 1
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    username = request.form.get('username', 'Anonymous')
    answer = request.form.get('q1')
    score = 100 if answer == '4' else 0
    
    new_score = QuizScore(username=username, score=score)
    db.session.add(new_score)
    db.session.commit()
    return redirect(url_for('index'))

# --- INITIALIZATION ---
def setup_database():
    with app.app_context():
        db.create_all()
        # Seed data if empty so the UI isn't blank on first load
        if not BlogPost.query.first():
            db.session.add(BlogPost(title="Welcome to the Learning Hub", content="This is our first mini-blog post. Feel free to like it!"))
            db.session.add(Poll(question="What is the best programming language for web APIs?", option_a="Python", option_b="PHP"))
            db.session.commit()

# Ensure database is set up when Render runs Gunicorn
setup_database()

if __name__ == '__main__':
    # Run locally
    app.run(debug=True)
