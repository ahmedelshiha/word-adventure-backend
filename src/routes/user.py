from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.models.user import User, db
from src.models.word import UserWordProgress, TestResult
from datetime import datetime
import re

user_bp = Blueprint('user', __name__)

def validate_email(email):
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Password validation - at least 6 characters"""
    return len(password) >= 6

@user_bp.route('/auth/register', methods=['POST'])
@cross_origin()
def register():
    """Register a new user"""
    try:
        data = request.json
        
        # Validate required fields
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data['username'].strip()
        password = data['password']
        email = data.get('email', '').strip()
        
        # Validate username
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        # Validate password
        if not validate_password(password):
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Validate email if provided
        if email and not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email already exists (if provided)
        if email and User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create new user
        user = User(username=username, email=email if email else None)
        user.set_password(password)
        
        # Initialize default virtual pet
        default_pet = {
            'name': 'Buddy',
            'type': 'cat',
            'happiness': 100,
            'growth': 0,
            'accessories': [],
            'lastFed': datetime.utcnow().timestamp() * 1000  # JavaScript timestamp
        }
        user.set_virtual_pet(default_pet)
        
        # Initialize default settings
        default_settings = {
            'fontSize': 'medium',
            'highContrast': False,
            'reducedMotion': False,
            'soundEnabled': True
        }
        user.set_settings(default_settings)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@user_bp.route('/auth/login', methods=['POST'])
@cross_origin()
def login():
    """Authenticate user login"""
    try:
        data = request.json
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user(user_id):
    """Get user profile"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get user', 'details': str(e)}), 500

@user_bp.route('/users/<int:user_id>/progress', methods=['PUT'])
@cross_origin()
def update_user_progress(user_id):
    """Update user progress data"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        
        if 'xp' in data:
            user.xp = max(0, data['xp'])
        if 'level' in data:
            user.level = max(1, data['level'])
        if 'words_learned' in data:
            user.words_learned = max(0, data['words_learned'])
        if 'current_streak' in data:
            user.current_streak = max(0, data['current_streak'])
            user.best_streak = max(user.best_streak, user.current_streak)
        if 'progress_data' in data:
            user.set_progress_data(data['progress_data'])
        if 'virtual_pet' in data:
            user.set_virtual_pet(data['virtual_pet'])
        if 'settings' in data:
            user.set_settings(data['settings'])
        if 'achievements' in data:
            user.set_achievements(data['achievements'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Progress updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update progress', 'details': str(e)}), 500

@user_bp.route('/users/<int:user_id>/word-progress', methods=['POST'])
@cross_origin()
def update_word_progress(user_id):
    """Update progress for a specific word"""
    try:
        data = request.json
        word_id = data.get('word_id')
        status = data.get('status', 'unknown')
        correct = data.get('correct', False)
        
        if not word_id:
            return jsonify({'error': 'word_id is required'}), 400
        
        # Find or create word progress record
        progress = UserWordProgress.query.filter_by(
            user_id=user_id, 
            word_id=word_id
        ).first()
        
        if not progress:
            progress = UserWordProgress(user_id=user_id, word_id=word_id)
            db.session.add(progress)
        
        # Update progress
        progress.status = status
        progress.attempts += 1
        progress.last_practiced = datetime.utcnow()
        
        if correct:
            progress.correct_attempts += 1
        
        # Calculate mastery level
        if progress.attempts > 0:
            progress.mastery_level = progress.correct_attempts / progress.attempts
        
        db.session.commit()
        
        return jsonify({
            'message': 'Word progress updated',
            'progress': progress.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update word progress', 'details': str(e)}), 500

@user_bp.route('/users/<int:user_id>/test-results', methods=['POST'])
@cross_origin()
def save_test_result(user_id):
    """Save a test result"""
    try:
        data = request.json
        
        test_result = TestResult(
            user_id=user_id,
            test_type=data.get('test_type', 'quiz'),
            score=data.get('score', 0),
            total_questions=data.get('total_questions', 0),
            time_taken=data.get('time_taken')
        )
        
        db.session.add(test_result)
        
        # Update user stats
        user = User.query.get(user_id)
        if user:
            user.total_tests_taken += 1
            
        db.session.commit()
        
        return jsonify({
            'message': 'Test result saved',
            'result': test_result.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to save test result', 'details': str(e)}), 500

@user_bp.route('/users/<int:user_id>/test-results', methods=['GET'])
@cross_origin()
def get_test_results(user_id):
    """Get user's test results"""
    try:
        results = TestResult.query.filter_by(user_id=user_id).order_by(
            TestResult.completed_at.desc()
        ).limit(50).all()
        
        return jsonify([result.to_dict() for result in results]), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get test results', 'details': str(e)}), 500

@user_bp.route('/users', methods=['GET'])
@cross_origin()
def get_users():
    """Get all users (admin function)"""
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get users', 'details': str(e)}), 500
