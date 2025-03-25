from flask import Flask, request, jsonify, render_template
import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from quizby.build  import build_sys_prompt, build_assistant_prompt, build_user_prompt
from quizby.quizby import quizby
import os
import PyPDF2
from werkzeug.utils import secure_filename

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
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
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
                if use_custom_textbook and 'textbook' in request.files:
                    file = request.files['textbook']
                    if file.filename:
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        
                        # Extract text from PDF if it's a PDF
                        if filename.lower().endswith('.pdf'):
                            textbook_content = extract_text_from_pdf(file_path)
                        elif filename.lower().endswith('.txt'):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                textbook_content = f.read()
                        
                        # Clean up the uploaded file
                        os.remove(file_path)
            else:
                # Handle JSON data
                data = request.json or {}
                custom_prompt = data.get('customPrompt', '')
                use_custom_textbook = data.get('useCustomTextbook', False)
                textbook_content = data.get('textbookContent')
            
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
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
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
