from flask import Flask, render_template, redirect, request, session, url_for, flash
from datetime import timedelta
import sqlite3

app = Flask(__name__)
app.secret_key = 'marwyvi'
app.permanent_session_lifetime = timedelta(minutes=9)
DATABASE = 'database.db'

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def register(self):
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (self.username, self.password))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def login(self):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (self.username,))
        record = cursor.fetchone()
        conn.close()
        if record and record[0] == self.password:
            return True
        return False

@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username, password)
        if user.login():
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username, password)
        if user.register():
            flash('Registration successful! You can now login.')
            return redirect(url_for('login'))
        else:
            flash('Username already exists.')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        release_year = request.form['release_year']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO movies (title, genre, date) VALUES (?, ?, ?)', (title, genre, release_year))
        conn.commit()
        conn.close()

        flash('Movie added successfully!')
        return redirect(url_for('movie_list'))

    return render_template('add_movie.html')

@app.route('/add_review/<int:movie_id>', methods=['GET', 'POST'])
def add_review(movie_id):
    if request.method == 'POST':
        review = request.form['review']
        rating = request.form['rating']
        user_id = session.get('user_id')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO reviews (user_id, movie_id, review, rating) VALUES (?, ?, ?, ?)',
                       (user_id, movie_id, review, rating))
        conn.commit()
        conn.close()

        flash('Review added successfully!')
        return redirect(url_for('movie', movie_id=movie_id))

    return render_template('add_review.html', movie_id=movie_id)

@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
    movie = cursor.fetchone()

    cursor.execute('SELECT * FROM reviews WHERE movie_id = ?', (movie_id,))
    reviews = cursor.fetchall()

    conn.close()
    return render_template('movie.html', movie=movie, reviews=reviews)

@app.route('/movie_list')
def movie_list():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM movies')
    movies = cursor.fetchall()
    conn.close()
    return render_template('movie_list.html', movies=movies)

if __name__ == '__main__':
    app.run(debug=True)
