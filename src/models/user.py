from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Word Adventure specific fields
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    words_learned = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    total_tests_taken = db.Column(db.Integer, default=0)
    
    # JSON fields for complex data
    progress_data = db.Column(db.Text, default='{}')  # Store learning progress as JSON
    settings = db.Column(db.Text, default='{}')  # Store user settings as JSON
    achievements = db.Column(db.Text, default='[]')  # Store achievements as JSON
    virtual_pet = db.Column(db.Text, default='{}')  # Store virtual pet data as JSON

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def get_progress_data(self):
        """Get progress data as Python dict"""
        try:
            return json.loads(self.progress_data) if self.progress_data else {}
        except:
            return {}

    def set_progress_data(self, data):
        """Set progress data from Python dict"""
        self.progress_data = json.dumps(data)

    def get_settings(self):
        """Get settings as Python dict"""
        try:
            return json.loads(self.settings) if self.settings else {}
        except:
            return {}

    def set_settings(self, data):
        """Set settings from Python dict"""
        self.settings = json.dumps(data)

    def get_achievements(self):
        """Get achievements as Python list"""
        try:
            return json.loads(self.achievements) if self.achievements else []
        except:
            return []

    def set_achievements(self, data):
        """Set achievements from Python list"""
        self.achievements = json.dumps(data)

    def get_virtual_pet(self):
        """Get virtual pet data as Python dict"""
        try:
            return json.loads(self.virtual_pet) if self.virtual_pet else {}
        except:
            return {}

    def set_virtual_pet(self, data):
        """Set virtual pet data from Python dict"""
        self.virtual_pet = json.dumps(data)

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary for API responses"""
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'level': self.level,
            'xp': self.xp,
            'words_learned': self.words_learned,
            'current_streak': self.current_streak,
            'best_streak': self.best_streak,
            'total_tests_taken': self.total_tests_taken,
            'progress_data': self.get_progress_data(),
            'settings': self.get_settings(),
            'achievements': self.get_achievements(),
            'virtual_pet': self.get_virtual_pet()
        }
        
        if include_sensitive:
            user_dict['password_hash'] = self.password_hash
            
        return user_dict
