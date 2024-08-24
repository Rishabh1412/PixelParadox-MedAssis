let medFirstMessageSent = false;

function prependmedMessage(sender, message) {
    const chatContainer = document.getElementById('med-chat-container-ai');
    const messageElement = document.createElement('div');
    messageElement.className = `med-chat-bubble ${sender === 'You' ? 'user' : 'bot'}`;
    messageElement.innerHTML = `${message}`;
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hidemedInitialElements() {
    document.getElementById('med-intro-text').classList.add('hidden');
}


async function sendmedMessage() {
    const imageInput = document.getElementById('med-image-input').files[0];

    if (imageInput) {
        // Display user's message
        prependmedMessage('You', ' - [Image]');

        if (!medFirstMessageSent) {
            hidemedInitialElements();
            medFirstMessageSent = true;
        }

        // Prepare data to send to the API
        const formData = new FormData();
        if (imageInput) {
            formData.append('uploaded_image', imageInput);
        }

        // Show loading spinner and hide send button text
        document.getElementById('med-loading-spinner').style.display = 'inline-block';
        document.getElementById('med-send-button-text').style.display = 'none';

        try {
            const response = await fetch('/api/medresponse', {
                method: 'POST',
                body: formData,
            });
            const result = await response.json();

            // Check if the response has an error
            if (response.ok) {
                prependmedMessage('AI', result.response);
            } else {
                prependmedMessage('AI', 'Sorry, something went wrong.');
                console.error('Error:', result.error);
            }
        } catch (error) {
            prependmedMessage('AI', 'Sorry, something went wrong.');
            console.error('Error:', error);
        }

        // Hide loading spinner and show send button text
        document.getElementById('loading-spinner').style.display = 'none';
        document.getElementById('send-button-text').style.display = 'inline-block';
    }
}

// Event listeners

document.getElementById('med-send-button-ai').addEventListener('click', sendmedMessage);
document.getElementById('med-image-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendmedMessage();
    }
});