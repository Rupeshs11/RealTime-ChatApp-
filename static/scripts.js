if (document.getElementById("chat-messages")) {
  const socket = io();

  const messageForm = document.getElementById("message-form");
  const messageInput = document.getElementById("message-input");
  const chatMessages = document.getElementById("chat-messages");
  const nicknameDisplay = document.getElementById("nickname-display");
  const roomDisplay = document.getElementById("room-display");

  const nickname = nicknameDisplay ? nicknameDisplay.textContent : "Anonymous";
  const room = roomDisplay
    ? roomDisplay.value || roomDisplay.textContent
    : "general";

  // Send message
  messageForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const message = messageInput.value.trim();

    if (message) {
      const now = new Date();
      const timestamp = now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });

      socket.emit("message", {
        nickname: nickname,
        message: message,
        room: room,
        timestamp: timestamp,
      });
      messageInput.value = "";
    }
  });

  // Connected - join room
  socket.on("connect", function () {
    socket.emit("join", { nickname: nickname, room: room });
    console.log("Connected to Socket.IO!");
  });

  // Load chat history from MongoDB
  socket.on("load_history", function (messages) {
    chatMessages.innerHTML = ""; // Clear "Loading messages..."

    if (messages.length === 0) {
      const emptyMsg = document.createElement("div");
      emptyMsg.classList.add("chat-message", "info");
      emptyMsg.innerHTML = "<em>No messages yet. Start the conversation!</em>";
      chatMessages.appendChild(emptyMsg);
    }

    messages.forEach(function (data) {
      renderMessage(data);
    });

    chatMessages.scrollTop = chatMessages.scrollHeight;
  });

  // Status messages (join/leave)
  socket.on("status", function (data) {
    const statusElement = document.createElement("div");
    statusElement.classList.add("chat-message", data.type);
    statusElement.innerHTML = `<em>${data.msg}</em>`;
    chatMessages.appendChild(statusElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  });

  // Incoming chat message
  socket.on("chat_message", function (data) {
    renderMessage(data);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  });

  // Render a single message
  function renderMessage(data) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("chat-message");

    if (data.nickname === nickname) {
      messageElement.classList.add("my-message");
    } else {
      messageElement.classList.add("other-message");
    }

    messageElement.innerHTML = `
            <span class="message-timestamp">${data.timestamp}</span>
            <span class="message-nickname">${data.nickname}:</span>
            <span class="message-text">${data.message}</span>
        `;
    chatMessages.appendChild(messageElement);
  }

  // Handle disconnect
  window.addEventListener("beforeunload", function () {
    socket.emit("leave", { nickname: nickname, room: room });
  });
}
