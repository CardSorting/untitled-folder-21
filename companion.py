import os
import uuid
from flask import Blueprint, render_template, request, jsonify, current_app, session
from flask_login import current_user, login_required
import google.generativeai as genai
from datetime import datetime
from companion_tasks import add_task, process_tasks, process_companion_chat
import json

companion_bp = Blueprint('companion', __name__, url_prefix='/companion')

# Configure Google Generative AI
genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-exp-1206')

def get_session_thread():
    """Get or create a thread ID for the current session"""
    if 'thread_id' not in session:
        session['thread_id'] = str(uuid.uuid4())
    return session['thread_id']

@companion_bp.route('/')
@login_required
def companion():
    """Render the AI companion page."""
    return render_template('companion/index.html')

@companion_bp.route('/chat-text')
@login_required
def companion_chat_text():
    """Render the AI companion text chat page."""
    # Ensure a thread ID exists for this session
    get_session_thread()
    return render_template('companion/chat.html')

@companion_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """Handle chat messages and return AI response."""
    try:
        data = request.json
        user_message = data.get('message')
        request_id = data.get('request_id', str(uuid.uuid4()))
        message_type = data.get('type', 'voice')
        thread_id = get_session_thread()
        
        if not user_message:
            return jsonify({'error': 'No message provided', 'request_id': request_id}), 400

        # Process chat message
        add_task(process_companion_chat, user_message, current_user.id, request_id, thread_id)
        process_tasks()
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'task_id': request_id # using request_id as a placeholder since we don't have a task id anymore
        })

    except Exception as e:
        current_app.logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'request_id': request_id if 'request_id' in locals() else None
        }), 500

    
@companion_bp.route('/history', methods=['GET'])
@login_required
def get_chat_history():
    """Get user's chat history for the current session."""
    try:
        limit = request.args.get('limit', default=50, type=int)
        thread_id = get_session_thread()
        messages = current_user.get_chat_history(limit=limit, thread_id=thread_id)
        
        return jsonify({
            'messages': messages
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting chat history: {str(e)}")
        return jsonify({'error': str(e)}), 500


@companion_bp.route('/stream')
@login_required
def stream():
    """SSE endpoint for real-time updates."""
    def generate():
        yield f"data: {json.dumps({'status': 'connected'})}\n\n" # send a connected message since we're not using redis anymore
    
    return current_app.response_class(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )
