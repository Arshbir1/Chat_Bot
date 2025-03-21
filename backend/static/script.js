// const recordButton = document.getElementById('recordButton');
// const sendButton = document.getElementById('sendButton');
// const textInput = document.getElementById('textInput');
// const chatMessages = document.getElementById('chatMessages');
// const errorDiv = document.getElementById('error');
// const languageSelect = document.getElementById('languageSelect');
// const clearChatButton = document.getElementById('clearChatButton');

// // These variables are set in the HTML script tag
// // const selectedCharacter = ...;
// // const ipAddress = ...;

// let isReloading = false;

// async function showLoading(isRecording = false) {
//     const loadingDiv = document.createElement('div');
//     loadingDiv.classList.add('loading-message');
//     loadingDiv.textContent = isRecording ? 'Recording & Processing...' : 'Processing...';
//     chatMessages.appendChild(loadingDiv);
//     chatMessages.scrollTop = chatMessages.scrollHeight;
//     return loadingDiv;
// }

// function removeLoading(loadingDiv) {
//     if (loadingDiv) loadingDiv.remove();
// }

// function syncConversation(conversation) {
//     chatMessages.innerHTML = '';
//     conversation.forEach(conv => {
//         addMessage(conv.user_input, true, conv.character, conv.recorded_audio_url);
//         addMessage(conv.response, false, conv.character, conv.synthesized_audio_url);
//     });
// }

// function addMessage(content, isUser, character = selectedCharacter, audioUrl = null) {
//     const messageDiv = document.createElement('div');
//     messageDiv.classList.add('message', isUser ? 'user' : 'character');
//     messageDiv.style.opacity = '0';

//     const messageContent = document.createElement('div');
//     messageContent.classList.add('message-content');
//     if (!isUser) {
//         messageContent.textContent = `${character.charAt(0).toUpperCase() + character.slice(1)}: ${content}`;
//     } else {
//         messageContent.textContent = content;
//     }

//     if (audioUrl) {
//         const audioContainer = document.createElement('div');
//         audioContainer.classList.add('audio-container');
//         const audio = document.createElement('audio');
//         audio.controls = true;
//         audio.src = audioUrl + '?t=' + new Date().getTime();
//         audio.autoplay = !isUser;
//         audioContainer.appendChild(audio);
//         messageContent.appendChild(audioContainer);
//     }

//     messageDiv.appendChild(messageContent);
//     chatMessages.appendChild(messageDiv);

//     setTimeout(() => {
//         messageDiv.style.transition = 'opacity 0.5s ease';
//         messageDiv.style.opacity = '1';
//     }, 10);

//     chatMessages.scrollTop = chatMessages.scrollHeight;
// }

// recordButton.addEventListener('click', async () => {
//     recordButton.disabled = true;
//     recordButton.innerHTML = 'Recording...';
//     errorDiv.style.display = 'none';
//     const loadingDiv = await showLoading(true);

//     try {
//         const response = await fetch('/process_audio', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ 
//                 character: selectedCharacter,
//                 language: languageSelect.value 
//             })
//         });

//         const data = await response.json();

//         if (response.ok) {
//             addMessage(data.transcript, true, data.character, data.recorded_audio_url);
//             addMessage(data.response, false, data.character, data.synthesized_audio_url);
//         } else {
//             errorDiv.textContent = data.error || 'An error occurred while processing the audio.';
//             errorDiv.style.display = 'block';
//         }
//     } catch (err) {
//         errorDiv.textContent = 'An error occurred: ' + err.message;
//         errorDiv.style.display = 'block';
//     } finally {
//         removeLoading(loadingDiv);
//         recordButton.disabled = false;
//         recordButton.innerHTML = '<img src="/static/mic_button.png" alt="Record" class="button-icon">';
//     }
// });

// sendButton.addEventListener('click', async () => {
//     const text = textInput.value.trim();
//     if (!text) return;

//     addMessage(text, true, selectedCharacter);
//     textInput.value = '';
//     errorDiv.style.display = 'none';
//     const loadingDiv = await showLoading();

//     try {
//         const response = await fetch('/process_text', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ 
//                 text, 
//                 character: selectedCharacter,
//                 language: languageSelect.value 
//             })
//         });

//         const data = await response.json();

//         if (response.ok) {
//             addMessage(data.response, false, data.character, data.synthesized_audio_url);
//         } else {
//             errorDiv.textContent = data.error || 'An error occurred while processing the text.';
//             errorDiv.style.display = 'block';
//         }
//     } catch (err) {
//         errorDiv.textContent = 'An error occurred: ' + err.message;
//         errorDiv.style.display = 'block';
//     } finally {
//         removeLoading(loadingDiv);
//     }
// });

// textInput.addEventListener('keypress', (e) => {
//     if (e.key === 'Enter') sendButton.click();
// });

// languageSelect.addEventListener('change', () => {
//     const selectedLanguage = languageSelect.options[languageSelect.selectedIndex].text;
//     errorDiv.textContent = `Language changed to ${selectedLanguage}`;
//     errorDiv.style.display = 'block';
//     errorDiv.style.color = 'green';
//     setTimeout(() => {
//         errorDiv.style.display = 'none';
//     }, 3000);
// });

// clearChatButton.addEventListener('click', async () => {
//     try {
//         const response = await fetch('/clear_chat', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ 
//                 ip_address: ipAddress,
//                 character: selectedCharacter 
//             })
//         });

//         const data = await response.json();

//         if (response.ok) {
//             chatMessages.innerHTML = '';
//             errorDiv.textContent = 'Chat cleared successfully!';
//             errorDiv.style.display = 'block';
//             errorDiv.style.color = 'green';
//             setTimeout(() => {
//                 errorDiv.style.display = 'none';
//             }, 3000);
//         } else {
//             errorDiv.textContent = data.error || 'Failed to clear chat.';
//             errorDiv.style.display = 'block';
//             errorDiv.style.color = 'red';
//         }
//     } catch (err) {
//         errorDiv.textContent = 'An error occurred: ' + err.message;
//         errorDiv.style.display = 'block';
//         errorDiv.style.color = 'red';
//     }
// });

// window.addEventListener('beforeunload', (event) => {
//     if (event.currentTarget.performance.navigation.type === 1) {
//         isReloading = true;
//     }
// });

// window.addEventListener('unload', () => {
//     if (!isReloading) {
//         const data = JSON.stringify({ ip_address: ipAddress, character: selectedCharacter });
//         const blob = new Blob([data], { type: 'application/json' });
//         navigator.sendBeacon('/cleanup', blob);
//     }
// });

// window.addEventListener('load', () => {
//     isReloading = false;
//     syncConversation(initialConversation);
// });























const recordButton = document.getElementById('recordButton');
const sendButton = document.getElementById('sendButton');
const textInput = document.getElementById('textInput');
const chatMessages = document.getElementById('chatMessages');
const errorDiv = document.getElementById('error');
const languageSelect = document.getElementById('languageSelect');
const clearChatButton = document.getElementById('clearChatButton');

// These variables are set in the HTML script tag
// const selectedCharacter = ...;
// const ipAddress = ...;

let isReloading = false;

async function showLoading(isRecording = false) {
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('loading-message');
    loadingDiv.textContent = isRecording ? 'Recording & Processing...' : 'Processing...';
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return loadingDiv;
}

function removeLoading(loadingDiv) {
    if (loadingDiv) loadingDiv.remove();
}

function syncConversation(conversation) {
    // Preserve the character-showcase div
    const characterShowcase = document.getElementById('characterShowcase');
    
    // Clear all messages except the character-showcase
    Array.from(chatMessages.children).forEach(child => {
        if (child !== characterShowcase) {
            child.remove();
        }
    });

    // Add the character-showcase back if it was removed (just in case)
    if (!chatMessages.contains(characterShowcase)) {
        chatMessages.insertBefore(characterShowcase, chatMessages.firstChild);
    }

    // Append conversation messages after the character-showcase
    conversation.forEach(conv => {
        addMessage(conv.user_input, true, conv.character, conv.recorded_audio_url);
        addMessage(conv.response, false, conv.character, conv.synthesized_audio_url);
    });
}

function addMessage(content, isUser, character = selectedCharacter, audioUrl = null) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', isUser ? 'user' : 'character');
    messageDiv.style.opacity = '0';

    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content');
    if (!isUser) {
        messageContent.textContent = `${character.charAt(0).toUpperCase() + character.slice(1)}: ${content}`;
    } else {
        messageContent.textContent = content;
    }

    if (audioUrl) {
        const audioContainer = document.createElement('div');
        audioContainer.classList.add('audio-container');
        const audio = document.createElement('audio');
        audio.controls = true;
        audio.src = audioUrl + '?t=' + new Date().getTime();
        audio.autoplay = !isUser;
        audioContainer.appendChild(audio);
        messageContent.appendChild(audioContainer);
    }

    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.style.transition = 'opacity 0.5s ease';
        messageDiv.style.opacity = '1';
    }, 10);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

recordButton.addEventListener('click', async () => {
    recordButton.disabled = true;
    recordButton.innerHTML = 'Recording...';
    errorDiv.style.display = 'none';
    const loadingDiv = await showLoading(true);

    try {
        const response = await fetch('/process_audio', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                character: selectedCharacter,
                language: languageSelect.value 
            })
        });

        const data = await response.json();

        if (response.ok) {
            addMessage(data.transcript, true, data.character, data.recorded_audio_url);
            addMessage(data.response, false, data.character, data.synthesized_audio_url);
        } else {
            errorDiv.textContent = data.error || 'An error occurred while processing the audio.';
            errorDiv.style.display = 'block';
        }
    } catch (err) {
        errorDiv.textContent = 'An error occurred: ' + err.message;
        errorDiv.style.display = 'block';
    } finally {
        removeLoading(loadingDiv);
        recordButton.disabled = false;
        recordButton.innerHTML = '<img src="/static/mic_button.png" alt="Record" class="button-icon">';
    }
});

sendButton.addEventListener('click', async () => {
    const text = textInput.value.trim();
    if (!text) return;

    addMessage(text, true, selectedCharacter);
    textInput.value = '';
    errorDiv.style.display = 'none';
    const loadingDiv = await showLoading();

    try {
        const response = await fetch('/process_text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                text, 
                character: selectedCharacter,
                language: languageSelect.value 
            })
        });

        const data = await response.json();

        if (response.ok) {
            addMessage(data.response, false, data.character, data.synthesized_audio_url);
        } else {
            errorDiv.textContent = data.error || 'An error occurred while processing the text.';
            errorDiv.style.display = 'block';
        }
    } catch (err) {
        errorDiv.textContent = 'An error occurred: ' + err.message;
        errorDiv.style.display = 'block';
    } finally {
        removeLoading(loadingDiv);
    }
});

textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendButton.click();
});

languageSelect.addEventListener('change', () => {
    const selectedLanguage = languageSelect.options[languageSelect.selectedIndex].text;
    errorDiv.textContent = `Language changed to ${selectedLanguage}`;
    errorDiv.style.display = 'block';
    errorDiv.style.color = 'green';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 3000);
});

clearChatButton.addEventListener('click', async () => {
    try {
        const response = await fetch('/clear_chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                ip_address: ipAddress,
                character: selectedCharacter 
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Clear messages but keep the character-showcase
            Array.from(chatMessages.children).forEach(child => {
                if (child.id !== 'characterShowcase') {
                    child.remove();
                }
            });
            errorDiv.textContent = 'Chat cleared successfully!';
            errorDiv.style.display = 'block';
            errorDiv.style.color = 'green';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 3000);
        } else {
            errorDiv.textContent = data.error || 'Failed to clear chat.';
            errorDiv.style.display = 'block';
            errorDiv.style.color = 'red';
        }
    } catch (err) {
        errorDiv.textContent = 'An error occurred: ' + err.message;
        errorDiv.style.display = 'block';
        errorDiv.style.color = 'red';
    }
});

window.addEventListener('beforeunload', (event) => {
    if (event.currentTarget.performance.navigation.type === 1) {
        isReloading = true;
    }
});

window.addEventListener('unload', () => {
    if (!isReloading) {
        const data = JSON.stringify({ ip_address: ipAddress, character: selectedCharacter });
        const blob = new Blob([data], { type: 'application/json' });
        navigator.sendBeacon('/cleanup', blob);
    }
});

window.addEventListener('load', () => {
    isReloading = false;
    syncConversation(initialConversation);
});






















