import datetime
import os

import PyPDF2
from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename

from quizby.build import build_assistant_prompt, build_sys_prompt, build_user_prompt
from quizby.quizby import quizby

# Configure limiter with Flask
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  # In-memory storage
)

def create_app(test_config=None):
    # Create Flask app
    app = Flask(__name__,
                template_folder='templates',  
                static_folder='static')
    
    # Load config
    app.config.from_object('config.Config')
    if test_config is not None:
        app.config.update(test_config)
    
    # Configure uploads
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    limiter.init_app(app)
    
    # Register routes directly in app
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')
    
    @app.route('/static/assets/<path:filename>')
    def serve_asset(filename):
        """Serve assets from static folder"""
        return app.send_static_file(f'assets/{filename}')

    @app.route('/generate-quiz', methods=['POST'])
    @limiter.limit("5 per hour")  # 5 requests per hour
    def generate_quiz():
        """Generate a quiz based on provided or default prompts"""
        try:
            # Handle different content types
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Handle file upload
                custom_prompt = request.form.get('customPrompt', '')
                use_custom_textbook = request.form.get('useCustomTextbook') == 'true'
                
                textbook_content = None
                if use_custom_textbook:
                    file = request.files.get('textbook')
                    if file is None or not file.filename:
                        raise ValueError('A PDF or TXT textbook upload is required.')

                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    try:
                        # Extract text from PDF if it's a PDF
                        if filename.lower().endswith('.pdf'):
                            textbook_content = extract_text_from_pdf(file_path)
                        elif filename.lower().endswith('.txt'):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                textbook_content = f.read()
                        else:
                            raise ValueError('Only PDF and TXT uploads are supported.')
                    finally:
                        if os.path.exists(file_path):
                            os.remove(file_path)
            else:
                # Handle JSON data
                if not request.is_json:
                    raise ValueError('Request must be JSON or multipart form data.')

                data = request.get_json(silent=True) or {}
                custom_prompt = data.get('customPrompt', '')
                use_custom_textbook = data.get('useCustomTextbook', False)
                textbook_content = data.get('textbookContent')
                if use_custom_textbook and not textbook_content:
                    raise ValueError('Custom textbook content is required when useCustomTextbook is true.')
            
            # Get base prompts
            system_prompt = build_sys_prompt()
            assistant_prompt = build_assistant_prompt(custom_textbook=textbook_content if use_custom_textbook else None)
            
            # Use custom or default user prompt
            user_prompt = custom_prompt if custom_prompt else build_user_prompt()
            
            # Track execution time
            start_time = datetime.datetime.now()
            
            # Generate content
            quiz_content = quizby(system_prompt, assistant_prompt, user_prompt, return_content=True)
            
            execution_time = datetime.datetime.now() - start_time
            
            return jsonify({
                'quiz': quiz_content,
                'executionTime': str(execution_time)
            })
        
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            app.logger.exception('Quiz generation failed')
            error_message = 'Unable to generate quiz right now. Please try again later.'
            if app.debug or app.testing:
                error_message = str(e)
            return jsonify({'error': error_message}), 500
    
    return app

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        text = f"Error extracting text from PDF: {str(e)}"
    
    return text
