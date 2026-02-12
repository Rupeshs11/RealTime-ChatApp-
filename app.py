from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from datetime import datetime
from functools import wraps
from config import MONGO_URI, SECRET_KEY, DB_NAME

# App Initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Initialize Flask-SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db['users']
messages_collection = db['messages']

# Create index for unique usernames
users_collection.create_index('username', unique=True)


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please login to continue.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== ROUTES ====================

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('join_room_page'))
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('join_room_page'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('signup.html')

        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'danger')
            return render_template('signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html')

        # Check if username exists
        if users_collection.find_one({'username': username}):
            flash('Username already taken. Try another one.', 'danger')
            return render_template('signup.html')

        # Create user
        users_collection.insert_one({
            'username': username,
            'password': generate_password_hash(password),
            'created_at': datetime.utcnow()
        })

        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('join_room_page'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter username and password.', 'danger')
            return render_template('login.html')

        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('join_room_page'))
        else:
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/join', methods=['GET', 'POST'])
@login_required
def join_room_page():
    if request.method == 'POST':
        room = request.form.get('room', '').strip()

        if not room:
            flash('Please enter a room name.', 'danger')
            return render_template('index.html', username=session['username'])

        session['room'] = room
        return redirect(url_for('chat'))

    return render_template('index.html', username=session['username'])


@app.route('/chat')
@login_required
def chat():
    if 'room' not in session:
        flash('Please select a room to join.', 'danger')
        return redirect(url_for('join_room_page'))

    return render_template('chat.html',
                           nickname=session['username'],
                           room=session['room'])


# ==================== SOCKET.IO EVENTS ====================

@socketio.on('join')
def on_join(data):
    nickname = data['nickname']
    room = data['room']

    join_room(room)

    # Load last 50 messages from MongoDB
    history = list(messages_collection.find(
        {'room': room},
        {'_id': 0, 'nickname': 1, 'message': 1, 'timestamp': 1}
    ).sort('created_at', -1).limit(50))

    history.reverse()

    # Send chat history to the user who just joined
    emit('load_history', history)

    # Notify room
    emit('status', {
        'msg': f'{nickname} has entered the room. Say Hello!',
        'type': 'info'
    }, to=room)

    print(f'{nickname} has joined room: {room}')


@socketio.on('leave')
def on_leave(data):
    nickname = data['nickname']
    room = data['room']

    leave_room(room)

    emit('status', {
        'msg': f'{nickname} has left the room. Bye bye!',
        'type': 'warning'
    }, to=room)

    print(f'{nickname} has left room: {room}')


@socketio.on('message')
def on_message(data):
    nickname = data['nickname']
    message = data['message']
    room = data['room']
    timestamp = data['timestamp']

    # Save message to MongoDB
    messages_collection.insert_one({
        'room': room,
        'nickname': nickname,
        'message': message,
        'timestamp': timestamp,
        'created_at': datetime.utcnow()
    })

    print(f'[{timestamp}] {nickname} in room {room}: {message}')

    emit('chat_message', {
        'nickname': nickname,
        'message': message,
        'timestamp': timestamp
    }, to=room)


@app.errorhandler(404)
def page_not_found(e):
    flash("Oops! That page does not exist.", "danger")
    return redirect(url_for('index'))


# Running the App
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)