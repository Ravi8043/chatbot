const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");

// Function to send a message
async function sendMessage() {
    const query = userInput.value.trim();
    if (!query) return;

    // Display user message
    addMessage(query, "user");

    try {
        const response = await fetch("http://127.0.0.1:8000/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query })
        });

        const data = await response.json();
        addMessage(data.response, "bot");
    } catch (error) {
        console.error("Error:", error);
        addMessage("Error fetching response. Try again!", "bot");
    }

    userInput.value = ""; // Clear input field
}

// Function to add messages to chat box
function addMessage(text, role) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", role === "user" ? "user-message" : "bot-message");
    messageDiv.textContent = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the latest message
}

// Function to send message when Enter key is pressed
function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}
