from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import json

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    
    def get_chat_history(self, limit=10, thread_id=None):
        """Get chat history for the user."""
        query = ChatMessage.query.filter_by(user_id=self.id)
        if thread_id:
            query = query.filter_by(thread_id=thread_id)
        messages = query.order_by(ChatMessage.timestamp.desc()).limit(limit).all()
        
        # Convert messages to a list of dictionaries
        history = []
        for msg in reversed(messages):
            history.append({
                'type': msg.message_type,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            })
        return history
    
    def save_message(self, user_message, ai_response, request_id, thread_id):
        """Save a chat message to the database."""
        user_msg = ChatMessage(
            user_id=self.id,
            content=user_message,
            message_type='user',
            request_id=request_id,
            thread_id=thread_id
        )
        ai_msg = ChatMessage(
            user_id=self.id,
            content=ai_response,
            message_type='ai',
            request_id=request_id,
            thread_id=thread_id
        )
        db.session.add(user_msg)
        db.session.add(ai_msg)
        db.session.commit()

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    request_id = db.Column(db.String(100), nullable=False)
    thread_id = db.Column(db.String(100), nullable=False)
    user = db.relationship('User', backref=db.backref('chat_messages', lazy=True))