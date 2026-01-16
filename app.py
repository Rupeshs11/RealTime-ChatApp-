from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
import os # For our secret key, because security is no laughing matter (well, sometimes it is)!


# App Initialization

app = Flask(__name__)

app.config['SECRET_KEY'] = 'This-is-a-secret-key'


# Initialize Flask-SocketIO

socketio = SocketIO(app, cors_allowed_origins="*")

# Routes
@app.route('/', methods = ['GET', 'POST'])
def index():
    
    if request.method == 'POST':
         #Accept user nickname
        nickname = request.form.get('nickname')
        
        room = request.form.get('room')
    
        if not nickname:

            flash('Please enter a nickname to join the chat', 'danger')
            
            return render_template('index.html')
        
        #Store the nickname andm room in session variable
        session['nickname'] = nickname
        session['room'] = room
        
        return redirect(url_for('chat'))
    
    # If Get method :
    return render_template('index.html')
    
@app.route('/chat')
def chat():
    
    if 'nickname' not in session or 'room' not in session:
        flash('Please enter a nickname namd room to access the chat.', 'danger')
        return redirect(url_for('index'))
    
    # Else Enter the chat room
    return render_template('chat.html', nickname = session['nickname'], room =  session['room'])

# SocketIO Event Handlers
@socketio.on('join')
def on_join(data):

    nickname = data['nickname']
    room = data['room']
    
    join_room(room) # Flask-SocketIO macgic! Puts the user into a specific "room"

    emit('status', {'msg': f'{nickname} has entered the room. Say Hello!', 'type': 'info'}, to = room)
    
    # Log it on the server side for debugging
    print(f'{nickname} has joined the : {room}') 


@socketio.on('leave')
def on_leave(data):
    
    nickname = data['nickname']
    room = data['room']
    
    leave_room(room) # Removes the user from the SocketIO room.
    
    emit('status', {'msg': f'{nickname} has left the room. Bye bye!', 'type': 'warning'}, to = room)
    
    print(f'{nickname} has left room: {room}')


@socketio.on('message')
def on_message(data):
    
    nickname = data['nickname']
    message = data['message']
    room = data['room']
    timestamp = data['timestamp']
    
    print(f'[{timestamp}] {nickname} in room {room}: {message}') #Server-side logging

    emit('chat_message', {'nickname': nickname, 'message': message, 'timestamp': timestamp}, to = room)
    

@app.errorhandler(404)
def page_not_found(e):
    
    flash("Oops! That page does not exist. Let's get you back to the chat.", "danger")
    return redirect(url_for('index'))



        
# Running the App

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)