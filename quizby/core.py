from flask import Flask, request, jsonify, render_template
import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from quizby.build  import build_sys_prompt, build_assistant_prompt, build_user_prompt
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
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(test_config)
    
    # Initialize extensions
    limiter.init_app(app)
    
    # Register routes directly in app
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')

    @app.route('/generate-quiz', methods=['POST'])
    @limiter.limit("5 per hour")  # 5 requests per hour
    def generate_quiz():
        """Generate a quiz based on provided or default prompts"""
        try:
            data = request.json or {}
            custom_prompt = data.get('customPrompt', '')
            
            # Get base prompts
            system_prompt = build_sys_prompt()
            assistant_prompt = build_assistant_prompt()
            
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
