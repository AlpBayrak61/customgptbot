document.addEventListener("DOMContentLoaded", () => {
    const uploadBtn = document.getElementById("uploadBtn");
    const fileInput = document.getElementById("fileInput");
    const uploadStatus = document.getElementById("uploadStatus");
    const chatContainer = document.getElementById("chatContainer");
    const chatWindow = document.getElementById("chatWindow");
    const userMessage = document.getElementById("userMessage");
    const sendMessage = document.getElementById("sendMessage");

    let fileId = null;

    // Upload the file
    uploadBtn.addEventListener("click", async () => {
        if (!fileInput.files[0]) {
            uploadStatus.textContent = "Please select a file to upload.";
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        uploadStatus.textContent = "Uploading file...";
        try {
            const response = await fetch("https://api.openai.com/v1/files", {
                method: "POST",
                headers: {
                    Authorization: `Bearer YOUR_API_KEY`,
                },
                body: formData,
            });

            const result = await response.json();
            fileId = result.id;
            uploadStatus.textContent = "File uploaded successfully!";
            chatContainer.classList.remove("hidden");
        } catch (error) {
            console.error(error);
            uploadStatus.textContent = "Failed to upload the file.";
        }
    });

    // Send a message
    sendMessage.addEventListener("click", async () => {
        const message = userMessage.value.trim();
        if (!message) return;

        // Display the user's message in the chat
        const userBubble = document.createElement("div");
        userBubble.textContent = `You: ${message}`;
        userBubble.classList.add("user");
        chatWindow.appendChild(userBubble);
        userMessage.value = "";

        // Call OpenAI API for assistant's response
        try {
            const response = await fetch("https://api.openai.com/v1/chat/completions", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer YOUR_API_KEY`,
                },
                body: JSON.stringify({
                    model: "gpt-4",
                    messages: [{ role: "user", content: message }],
                }),
            });

            const result = await response.json();
            const assistantMessage = result.choices[0].message.content;

            // Display the assistant's message in the chat
            const assistantBubble = document.createElement("div");
            assistantBubble.textContent = `Assistant: ${assistantMessage}`;
            assistantBubble.classList.add("assistant");
            chatWindow.appendChild(assistantBubble);
            chatWindow.scrollTop = chatWindow.scrollHeight;
        } catch (error) {
            console.error(error);
            const errorBubble = document.createElement("div");
            errorBubble.textContent = "Error: Unable to get a response.";
            errorBubble.classList.add("assistant");
            chatWindow.appendChild(errorBubble);
        }
    });
});
