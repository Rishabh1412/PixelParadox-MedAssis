document.addEventListener("DOMContentLoaded", function () {
  const socket = io();
  const chatInput = document.getElementById("chat-input-user");
  const sendButton = document.getElementById("send-button-user");
  const chatWindow = document.getElementById("chat-window-user");
  const currentUser = chatWindow.getAttribute("data-username");

  // Load messages from the server when the page loads
  loadMessagesFromDatabase();

  sendButton.addEventListener("click", sendMessageUser);
  chatInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      sendMessageUser();
    }
  });

  function sendMessageUser() {
    const message = chatInput.value.trim();
    if (message !== "") {
      const timestamp = new Date().toISOString();  // Ensure timestamp is in ISO format
      socket.emit('send_message', { message: message, timestamp: timestamp });
      chatInput.value = "";
    }
  }

  socket.on('receive_message', function (data) {
    const isCurrentUser = data.username === currentUser;
    appendMessageUser(data.message, data.username, data.timestamp, isCurrentUser ? 'user' : 'bot');
  });

  function appendMessageUser(message, username, timestamp, sender) {
    const messageContainer = document.createElement("div");
    messageContainer.classList.add("message", sender);

    const userText = document.createElement("span");
    userText.textContent = username;
    userText.classList.add("username");

    const messageText = document.createElement("span");
    messageText.textContent = message;
    messageText.classList.add("message-text");

    const messageTimestamp = document.createElement("span");
    messageTimestamp.classList.add("timestamp");
    messageTimestamp.textContent = new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    messageContainer.appendChild(userText);
    messageContainer.appendChild(messageText);
    messageContainer.appendChild(messageTimestamp);

    chatWindow.appendChild(messageContainer);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function loadMessagesFromDatabase() {
    fetch('/load_messages')  // Adjust the endpoint to your Flask route
      .then(response => response.json())
      .then(data => {
        data.messages.forEach(messageData => {
          const isCurrentUser = messageData.username === currentUser;
          appendMessageUser(
            messageData.content,
            messageData.username,
            messageData.timestamp,
            isCurrentUser ? 'user' : 'bot'
          );
        });
      })
      .catch(error => console.error('Error loading messages:', error));
  }
});
