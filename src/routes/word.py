from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.models.word import Word, UserWordProgress, db
from src.models.user import User
from datetime import datetime

word_bp = Blueprint('word', __name__)

@word_bp.route('/words', methods=['GET'])
@cross_origin()
def get_words():
    """Get all words with optional filtering"""
    try:
        # Get query parameters
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        user_id = request.args.get('user_id')
        
        # Build query
        query = Word.query
        
        if category and category != 'all':
            query = query.filter(Word.category == category)
        
        if difficulty and difficulty != 'all':
            query = query.filter(Word.difficulty == difficulty)
        
        words = query.order_by(Word.word).all()
        
        # If user_id is provided, include user progress
        if user_id:
            word_list = []
            for word in words:
                word_dict = word.to_dict()
                
                # Get user progress for this word
                progress = UserWordProgress.query.filter_by(
                    user_id=user_id, 
                    word_id=word.id
                ).first()
                
                if progress:
                    word_dict['user_progress'] = progress.to_dict()
                else:
                    word_dict['user_progress'] = {
                        'status': 'unknown',
                        'attempts': 0,
                        'correct_attempts': 0,
                        'mastery_level': 0.0
                    }
                
                word_list.append(word_dict)
            
            return jsonify(word_list), 200
        else:
            return jsonify([word.to_dict() for word in words]), 200
            
    except Exception as e:
        return jsonify({'error': 'Failed to get words', 'details': str(e)}), 500

@word_bp.route('/words/<int:word_id>', methods=['GET'])
@cross_origin()
def get_word(word_id):
    """Get a specific word"""
    try:
        word = Word.query.get_or_404(word_id)
        return jsonify(word.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get word', 'details': str(e)}), 500

@word_bp.route('/words', methods=['POST'])
@cross_origin()
def create_word():
    """Create a new word"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['word', 'definition', 'category', 'difficulty']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if word already exists
        existing_word = Word.query.filter_by(word=data['word'].lower()).first()
        if existing_word:
            return jsonify({'error': 'Word already exists'}), 409
        
        # Create new word
        word = Word(
            word=data['word'].lower(),
            pronunciation=data.get('pronunciation'),
            definition=data['definition'],
            example=data.get('example'),
            fun_fact=data.get('fun_fact'),
            image_url=data.get('image_url'),
            emoji=data.get('emoji'),
            category=data['category'],
            difficulty=data['difficulty']
        )
        
        db.session.add(word)
        db.session.commit()
        
        return jsonify({
            'message': 'Word created successfully',
            'word': word.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create word', 'details': str(e)}), 500

@word_bp.route('/words/bulk', methods=['POST'])
@cross_origin()
def create_words_bulk():
    """Create multiple words from CSV data"""
    try:
        data = request.json
        words_data = data.get('words', [])
        
        if not words_data:
            return jsonify({'error': 'No words data provided'}), 400
        
        created_words = []
        errors = []
        
        for i, word_data in enumerate(words_data):
            try:
                # Validate required fields
                if not word_data.get('word') or not word_data.get('definition'):
                    errors.append(f"Row {i+1}: Word and definition are required")
                    continue
                
                # Check if word already exists
                existing_word = Word.query.filter_by(word=word_data['word'].lower()).first()
                if existing_word:
                    errors.append(f"Row {i+1}: Word '{word_data['word']}' already exists")
                    continue
                
                # Create word
                word = Word(
                    word=word_data['word'].lower(),
                    pronunciation=word_data.get('pronunciation'),
                    definition=word_data['definition'],
                    example=word_data.get('example'),
                    fun_fact=word_data.get('fun_fact'),
                    image_url=word_data.get('image_url'),
                    emoji=word_data.get('emoji'),
                    category=word_data.get('category', 'general'),
                    difficulty=word_data.get('difficulty', 'medium')
                )
                
                db.session.add(word)
                created_words.append(word_data['word'])
                
            except Exception as e:
                errors.append(f"Row {i+1}: {str(e)}")
        
        if created_words:
            db.session.commit()
        
        return jsonify({
            'message': f'Bulk import completed',
            'created': len(created_words),
            'errors': len(errors),
            'created_words': created_words,
            'error_details': errors
        }), 201 if created_words else 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Bulk import failed', 'details': str(e)}), 500

@word_bp.route('/categories', methods=['GET'])
@cross_origin()
def get_categories():
    """Get all word categories"""
    try:
        categories = db.session.query(Word.category).distinct().all()
        category_list = [cat[0] for cat in categories]
        return jsonify(category_list), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get categories', 'details': str(e)}), 500

@word_bp.route('/difficulties', methods=['GET'])
@cross_origin()
def get_difficulties():
    """Get all difficulty levels"""
    try:
        difficulties = db.session.query(Word.difficulty).distinct().all()
        difficulty_list = [diff[0] for diff in difficulties]
        return jsonify(difficulty_list), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get difficulties', 'details': str(e)}), 500

@word_bp.route('/words/random', methods=['GET'])
@cross_origin()
def get_random_words():
    """Get random words for quizzes"""
    try:
        count = request.args.get('count', 10, type=int)
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        user_id = request.args.get('user_id')
        
        # Build query
        query = Word.query
        
        if category and category != 'all':
            query = query.filter(Word.category == category)
        
        if difficulty and difficulty != 'all':
            query = query.filter(Word.difficulty == difficulty)
        
        # Get random words
        words = query.order_by(db.func.random()).limit(count).all()
        
        # Include user progress if user_id provided
        if user_id:
            word_list = []
            for word in words:
                word_dict = word.to_dict()
                
                progress = UserWordProgress.query.filter_by(
                    user_id=user_id, 
                    word_id=word.id
                ).first()
                
                if progress:
                    word_dict['user_progress'] = progress.to_dict()
                
                word_list.append(word_dict)
            
            return jsonify(word_list), 200
        else:
            return jsonify([word.to_dict() for word in words]), 200
            
    except Exception as e:
        return jsonify({'error': 'Failed to get random words', 'details': str(e)}), 500

@word_bp.route('/words/search', methods=['GET'])
@cross_origin()
def search_words():
    """Search words by term"""
    try:
        search_term = request.args.get('q', '').strip()
        
        if not search_term:
            return jsonify([]), 200
        
        # Search in word, definition, and example
        words = Word.query.filter(
            db.or_(
                Word.word.contains(search_term.lower()),
                Word.definition.contains(search_term),
                Word.example.contains(search_term)
            )
        ).order_by(Word.word).limit(50).all()
        
        return jsonify([word.to_dict() for word in words]), 200
        
    except Exception as e:
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500

