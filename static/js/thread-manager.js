class ThreadManager {
    constructor() {
        this.messageCallbacks = [];
        this.threadId = null;
        this.loadChatHistory();
    }

    async sendMessage(message) {
        const request_id = this.generateUUID();
        try {
            const response = await fetch('/companion/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message, request_id: request_id }),
            });

            if (!response.ok) {
                const error = await response.json();
                console.error('Error sending message:', error);
                this.showAlert('Error sending message', 'error');
                return;
            }

            const data = await response.json();
            if (data.success) {
                this.fetchResponse(data.task_id);
            } else {
                 console.error('Error sending message:', data);
                 this.showAlert('Error sending message', 'error');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.showAlert('Error sending message', 'error');
        }
    }
    
    async fetchResponse(taskId) {
        try {
            const response = await fetch(`/companion/history?limit=1`);
            if (!response.ok) {
                const error = await response.json();
                console.error('Error fetching response:', error);
                this.showAlert('Error fetching response', 'error');
                return;
            }
            const data = await response.json();
            if (data.messages && data.messages.length > 0) {
                const lastMessage = data.messages[0];
                if (lastMessage.type === 'ai') {
                    this.messageCallbacks.forEach(callback => callback({ response: lastMessage.content }));
                }
            }
        } catch (error) {
            console.error('Error fetching response:', error);
            this.showAlert('Error fetching response', 'error');
        }
    }

    onMessage(callback) {
        this.messageCallbacks.push(callback);
    }
    
    async loadChatHistory() {
        try {
            const response = await fetch('/companion/history');
            if (!response.ok) {
                const error = await response.json();
                 console.error('Error loading chat history:', error);
                 this.showAlert('Error loading chat history', 'error');
                return;
            }
            const data = await response.json();
            if (data.messages) {
                data.messages.forEach(msg => {
                    if (msg.type === 'user') {
                        const userMessageTemplate = document.getElementById('userMessageTemplate').content.cloneNode(true);
                        userMessageTemplate.querySelector('p').textContent = msg.content;
                        document.getElementById('chatMessages').appendChild(userMessageTemplate);
                    } else if (msg.type === 'ai') {
                        const aiMessageTemplate = document.getElementById('aiMessageTemplate').content.cloneNode(true);
                        aiMessageTemplate.querySelector('p').textContent = msg.content;
                        document.getElementById('chatMessages').appendChild(aiMessageTemplate);
                    }
                });
                this.scrollToBottom();
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
            this.showAlert('Error loading chat history', 'error');
        }
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('messagesContainer');
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }
    
    generateUUID() {
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
    }
    
    showAlert(message, type = 'success') {
        const alertContainer = document.getElementById('alert-container');
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} pointer-events-auto`;
        alertDiv.textContent = message;
        alertContainer.appendChild(alertDiv);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }
}
