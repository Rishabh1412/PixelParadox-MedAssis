let firstMessageSent = false;

function prependMessage(sender, message) {
    const chatContainer = document.getElementById('chat-container-ai');
    const messageElement = document.createElement('div');
    messageElement.className = `chat-bubble ${sender === 'You' ? 'user' : 'bot'}`;
    messageElement.innerHTML = `${message}`;

    chatContainer.appendChild(messageElement);

    // Automatically scroll to the bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function getAIResponse(prompt) {
    return fetch('/api/get_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: prompt }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                return 'Sorry, something went wrong.';
            }
            return data.response;
        })
        .catch(error => {
            console.error('Error:', error);
            return 'Sorry, something went wrong.';
        });
}

function hideInitialElements() {
    document.getElementById('intro-text').classList.add('hidden');
    document.getElementById('cards-container').classList.add('hidden');
}

async function sendMessage() {
    const inputField = document.getElementById('user-prompt');
    const userMessage = inputField.value.trim();

    if (userMessage) {
        prependMessage('You', userMessage);
        inputField.value = '';

        if (!firstMessageSent) {
            hideInitialElements();
            firstMessageSent = true;
        }

        const aiResponse = await getAIResponse(userMessage);
        prependMessage('AI', aiResponse);
    }
}

function handleP1Click() {
    document.getElementById('user-prompt').value = document.querySelector('.p1_text').innerText;
    sendMessage();
}

function handleP2Click() {
    document.getElementById('user-prompt').value = document.querySelector('.p2_text').innerText;
    sendMessage();
}

function handleP3Click() {
    document.getElementById('user-prompt').value = document.querySelector('.p3_text').innerText;
    sendMessage();
}

document.getElementById('send-button-ai').addEventListener('click', sendMessage);
document.getElementById('user-prompt').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
