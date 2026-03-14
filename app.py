from flask import Flask, render_template, request, redirect, url_for
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

# --- ROUTES ---
@app.route('/')
def index():
    posts = BlogPost.query.order_by(BlogPost.id.desc()).all()
    polls = Poll.query.all()
    scores = QuizScore.query.order_by(QuizScore.score.desc()).limit(5).all()
    return render_template('index.html', posts=posts, polls=polls, scores=scores)

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
    # Simple hardcoded quiz logic for demonstration
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
        # Seed data if empty
        if not BlogPost.query.first():
            db.session.add(BlogPost(title="Welcome to the Learning Hub", content="This is our first mini-blog post. Feel free to like it!"))
            db.session.add(Poll(question="What is the best programming language for web APIs?", option_a="Python", option_b="PHP"))
            db.session.commit()

if __name__ == '__main__':
    setup_database()
    # Run locally
    app.run(debug=True)
else:
    # Gunicorn setup
    setup_database()
