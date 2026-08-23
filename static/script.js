const micBtn = document.getElementById('mic-btn');
const statusText = document.getElementById('status-text');
const feedbackToast = document.getElementById('feedback-toast');
const toastMessage = document.getElementById('toast-message');
const emptyState = document.getElementById('empty-state');
const shoppingCategories = document.getElementById('shopping-categories');
const suggestionsContainer = document.getElementById('suggestions-container');
const suggestionsList = document.getElementById('suggestions-list');

let isListening = false;
let recognition = null;

// Initialize Web Speech API
if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false; // Stop after one phrase
    recognition.lang = 'en-US'; // Multi-language can be switched here
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = function() {
        isListening = true;
        micBtn.classList.add('listening');
        statusText.textContent = "Listening...";
    };

    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        statusText.textContent = `Heard: "${text}"`;
        processCommand(text);
    };

    recognition.onerror = function(event) {
        statusText.textContent = "Error: " + event.error;
        stopListening();
    };

    recognition.onend = function() {
        stopListening();
        if (statusText.textContent === "Listening...") {
            statusText.textContent = "Tap to speak...";
        }
    };
} else {
    statusText.textContent = "Speech Recognition not supported in this browser.";
    micBtn.disabled = true;
}

micBtn.addEventListener('click', () => {
    if (isListening) {
        recognition.stop();
    } else {
        recognition.start();
    }
});

function stopListening() {
    isListening = false;
    micBtn.classList.remove('listening');
}

function showToast(message, isError = false) {
    toastMessage.textContent = message;
    if (isError) {
        feedbackToast.classList.add('danger');
    } else {
        feedbackToast.classList.remove('danger');
    }
    
    feedbackToast.classList.remove('hidden');
    setTimeout(() => {
        feedbackToast.classList.add('hidden');
    }, 3000);
}

// Process voice text via Flask backend
async function processCommand(text) {
    try {
        statusText.textContent = "Processing...";
        const response = await fetch('/api/process-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast(data.message, data.action === 'unknown');
            setTimeout(() => { statusText.textContent = "Tap to speak..."; }, 2000);
            
            if (data.current_list) {
                renderList(data.current_list);
            }
            if (data.list_updated) {
                fetchSuggestions();
            }
        }
    } catch (err) {
        console.error(err);
        showToast("Network error. Please try again.", true);
        statusText.textContent = "Tap to speak...";
    }
}

// Fetch smart suggestions
async function fetchSuggestions() {
    try {
        const res = await fetch('/api/suggestions');
        const data = await res.json();
        if (data.suggestions && data.suggestions.length > 0) {
            renderSuggestions(data.suggestions);
        } else {
            suggestionsContainer.classList.add('hidden');
        }
    } catch (e) {
        console.error("Failed to fetch suggestions");
    }
}

async function addSuggestedItem(itemName) {
    try {
        const response = await fetch('/api/add-item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item: itemName })
        });
        const data = await response.json();
        if(data.status === 'success') {
            renderList(data.current_list);
            showToast(data.message);
            fetchSuggestions();
        }
    } catch (e) {
        showToast("Error adding item", true);
    }
}

function renderSuggestions(suggestions) {
    suggestionsList.innerHTML = '';
    suggestionsContainer.classList.remove('hidden');
    
    suggestions.forEach(s => {
        const div = document.createElement('div');
        div.className = 'suggestion-item';
        div.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 5px;">
                <strong>${s.item}</strong>
                <p>${s.text}</p>
            </div>
            <button onclick="addSuggestedItem('${s.item}')">Add to List</button>
        `;
        suggestionsList.appendChild(div);
    });
}

function renderList(items) {
    if (items.length === 0) {
        emptyState.classList.remove('hidden');
        shoppingCategories.innerHTML = '';
        return;
    }
    
    emptyState.classList.add('hidden');
    
    // Group by category
    const grouped = {};
    items.forEach(item => {
        if (!grouped[item.category]) grouped[item.category] = [];
        grouped[item.category].push(item);
    });
    
    shoppingCategories.innerHTML = '';
    
    for (const [category, catItems] of Object.entries(grouped)) {
        const catDiv = document.createElement('div');
        catDiv.className = 'category-block';
        
        const h4 = document.createElement('h4');
        h4.innerHTML = `${category} <span>${catItems.length} items</span>`;
        catDiv.appendChild(h4);
        
        catItems.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'category-item';
            itemDiv.innerHTML = `
                <div class="item-details">
                    <div class="item-qty">${item.quantity}</div>
                    <div class="item-name">${item.name}</div>
                </div>
            `;
            catDiv.appendChild(itemDiv);
        });
        
        shoppingCategories.appendChild(catDiv);
    }
}

// Initial fetch
fetch('/api/list').then(r => r.json()).then(d => renderList(d.current_list));
fetchSuggestions();
