from src.models.user import db
from datetime import datetime

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    pronunciation = db.Column(db.String(200))
    definition = db.Column(db.Text, nullable=False)
    example = db.Column(db.Text)
    fun_fact = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    emoji = db.Column(db.String(10))
    category = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # easy, medium, hard
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Word {self.word}>'

    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
            'pronunciation': self.pronunciation,
            'definition': self.definition,
            'example': self.example,
            'fun_fact': self.fun_fact,
            'image_url': self.image_url,
            'emoji': self.emoji,
            'category': self.category,
            'difficulty': self.difficulty,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserWordProgress(db.Model):
    """Track individual user progress on specific words"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    status = db.Column(db.String(20), default='unknown')  # unknown, learning, known
    attempts = db.Column(db.Integer, default=0)
    correct_attempts = db.Column(db.Integer, default=0)
    last_practiced = db.Column(db.DateTime, default=datetime.utcnow)
    mastery_level = db.Column(db.Float, default=0.0)  # 0.0 to 1.0

    def __repr__(self):
        return f'<UserWordProgress user_id={self.user_id} word_id={self.word_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'word_id': self.word_id,
            'status': self.status,
            'attempts': self.attempts,
            'correct_attempts': self.correct_attempts,
            'last_practiced': self.last_practiced.isoformat() if self.last_practiced else None,
            'mastery_level': self.mastery_level,
            'word': self.word.to_dict() if hasattr(self, 'word') and self.word else None
        }

class TestResult(db.Model):
    """Store quiz/test results"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)  # quiz, speed_challenge, etc.
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer)  # in seconds
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TestResult user_id={self.user_id} score={self.score}/{self.total_questions}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'test_type': self.test_type,
            'score': self.score,
            'total_questions': self.total_questions,
            'time_taken': self.time_taken,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'accuracy': round((self.score / self.total_questions) * 100, 2) if self.total_questions > 0 else 0
        }

