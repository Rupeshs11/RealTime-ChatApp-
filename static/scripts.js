if (document.getElementById('chat-messages')){
    // Connect to the Socket.IO server

    const socket = io();

    // Get references to our HTML elements
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const nicknameDisplay = document.getElementById('nickname-display');
    const roomDisplay = document.getElementById('room-display');

    const nickname = nicknameDisplay ? nicknameDisplay.textContent: 'Anonymous';
    const room = roomDisplay? roomDisplay.textContent : 'general'

    // When the message form is submitted
    messageForm.addEventListener('submit', function(e){

        e.preventDefault(); // Stop the browser from doing its default form submission (Page Re-load)

        const message = messageInput.value.trim(); // Get the message text and remove leading spaces


        if(message){ // Only send if there's an actual message. No Empty Echoes
            const now = new Date();
            const timestamp = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            // Emit a 'message' event to the server
            socket.emit('message', {
                'nickname': nickname,
                'message': message,
                'room': room,
                'timestamp': timestamp
            });
            messageInput.value = ''; 
        }
    });


    // Socket.io event handlers (reacting to Server Messages)

    socket.on('connect', function(){

        // Immediately send a 'Join' event to the Server
        socket.emit('join', {'nickname': nickname, 'room': room });
        console.log('Connected to Socket.IO!')

    });


    socket.on('status', function(data){
        const statusElement = document.createElement('div'); // Creating a New Div Element for the status message

        statusElement.classList.add('chat-message', data.type); // Adding a class for styling

        statusElement.innerHTML = `<em>${data.msg}</em>`; // Display the status message

        chatMessages.appendChild(statusElement); // Add it to out chat messages container

        chatMessages.scrollTop = chatMessages.scrollHeight; // Scrolling to the bottom to see the latest message 
    });


    // When the server sends a 'chat_message' event
    socket.on('chat_message', function(data){

        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message'); // Basic class for styling.

        // If the message is from us, give it a special class for styling (e.g., different background).
        if (data.nickname === nickname) {
            messageElement.classList.add('my-message');
        } else {
            messageElement.classList.add('other-message');
        }

        // Construct the message HTML.
        messageElement.innerHTML = `
            <span class="message-timestamp">${data.timestamp}</span>
            <span class="message-nickname">${data.nickname}:</span>
            <span class="message-text">${data.message}</span>
        `;
        chatMessages.appendChild(messageElement); // Add it to the display.
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll down, always keep the latest in view!

    });


    // Handel Disconnect
    window.addEventListener('beforeunload', function(){
        socket.emit('leave', {'nickname': nickname, 'room': room});
    });
}