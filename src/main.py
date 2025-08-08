import os
import sys

# Ensure src/ is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.models.word import Word, UserWordProgress, TestResult
from src.routes.user import user_bp
from src.routes.word import word_bp

# Create Flask app
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# ✅ Allow only your Netlify frontend
CORS(app, origins=["https://words-adventure.netlify.app"], supports_credentials=True)

# Register Blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(word_bp, url_prefix='/api')

# Configure PostgreSQL database from environment
database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("❌ DATABASE_URL environment variable not found!")
    # Fallback to SQLite for local development
    database_url = "sqlite:///word_adventure.db"
    print("🔄 Using SQLite fallback database")

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

def seed_database(force_reseed=False):
    """Seed the database with 200 comprehensive words if empty or force re-seed"""
    print("Attempting to seed database...")
    try:
        if force_reseed:
            print("Force re-seeding: Deleting existing words...")
            db.session.query(Word).delete()
            db.session.commit()
            print("Existing words deleted.")

        if Word.query.count() == 0 or force_reseed:
            # Import the comprehensive 200-word dataset
            from data.words_200 import words_data
            
            print(f"Adding {len(words_data)} words to database...")
            for word_data in words_data:
                word = Word(**word_data)
                db.session.add(word)

            db.session.commit()
            print(f"✅ Database seeded with {len(words_data)} comprehensive words!")
            return True
        else:
            print("✅ Database already contains words")
            return True
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        db.session.rollback()
        return False

# Initialize database with app context
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully")
        seed_database()
    except Exception as e:
        print(f"❌ Database initialization error: {str(e)}")

# Health check route
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        word_count = Word.query.count()
        return {
            'status': 'healthy', 
            'message': 'Word Adventure API is running!',
            'database': 'connected',
            'word_count': word_count
        }, 200
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': 'Database connection failed',
            'error': str(e)
        }, 500

# Database initialization endpoint (for manual seeding)
@app.route('/api/init-db', methods=['POST'])
def init_database():
    try:
        db.create_all()
        success = seed_database(force_reseed=True) # Force re-seed on manual trigger
        if success:
            return {
                'status': 'success',
                'message': 'Database initialized and seeded successfully'
            }, 200
        else:
            return {
                'status': 'error',
                'message': 'Database seeding failed'
            }, 500
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Database initialization failed: {str(e)}'
        }, 500

# Serve static files (optional)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if not static_folder_path:
        return "Static folder not configured", 404

    requested_path = os.path.join(static_folder_path, path)

    if path and os.path.exists(requested_path):
        return send_from_directory(static_folder_path, path)
    
    index_path = os.path.join(static_folder_path, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, 'index.html')
    
    return "index.html not found", 404

# For local testing only
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


