let newFirstMessageSent = false;

function prependNewMessage(sender, message) {
    const chatContainer = document.getElementById('new-chat-container-ai');
    const messageElement = document.createElement('div');
    messageElement.className = `new-chat-bubble ${sender === 'You' ? 'user' : 'bot'}`;
    messageElement.innerHTML = `${message}`;
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideNewInitialElements() {
    document.getElementById('new-intro-text').classList.add('hidden');
}

function toggleInputFields() {
    const inputType = document.getElementById('input-type-select').value;
    document.getElementById('new-user-prompt').style.display = inputType === 'text' ? 'block' : 'none';
    document.getElementById('image-input').style.display = inputType === 'image' ? 'block' : 'none';
}

async function sendNewMessage() {
    const diseaseInput = document.getElementById('disease-input').value.trim();
    const inputType = document.getElementById('input-type-select').value;
    const userMessage = document.getElementById('new-user-prompt').value.trim();
    const imageInput = document.getElementById('image-input').files[0];

    if (diseaseInput && (userMessage || imageInput)) {
        // Display user's message
        prependNewMessage('You', diseaseInput + (inputType === 'text' ? ` - ${userMessage}` : ' - [Image]'));

        if (!newFirstMessageSent) {
            hideNewInitialElements();
            newFirstMessageSent = true;
        }

        // Prepare data to send to the API
        const formData = new FormData();
        formData.append('disease', diseaseInput);
        formData.append('input_type', inputType === 'text' ? 'Text Prompt' : 'Image');
        formData.append('user_input', userMessage);
        if (imageInput) {
            formData.append('uploaded_image', imageInput);
        }

        // Show loading spinner and hide send button text
        document.getElementById('loading-spinner').style.display = 'inline-block';
        document.getElementById('send-button-text').style.display = 'none';

        try {
            const response = await fetch('/api/foodResponse', {
                method: 'POST',
                body: formData,
            });
            const result = await response.json();

            // Check if the response has an error
            if (response.ok) {
                prependNewMessage('AI', result.response);
            } else {
                prependNewMessage('AI', 'Sorry, something went wrong.');
                console.error('Error:', result.error);
            }
        } catch (error) {
            prependNewMessage('AI', 'Sorry, something went wrong.');
            console.error('Error:', error);
        }

        // Hide loading spinner and show send button text
        document.getElementById('loading-spinner').style.display = 'none';
        document.getElementById('send-button-text').style.display = 'inline-block';
    }
}

// Event listeners
document.getElementById('input-type-select').addEventListener('change', toggleInputFields);
document.getElementById('new-send-button-ai').addEventListener('click', sendNewMessage);
document.getElementById('new-user-prompt').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendNewMessage();
    }
});
