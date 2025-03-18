from flask import Flask, Blueprint, render_template, request, jsonify, current_app, session
import datetime
import logging
import time
from quizby import quizby, build_sys_prompt, build_assistant_prompt, build_user_prompt
from functools import wraps

logger = logging.getLogger(__name__)

# In-memory rate limiter - will reset on app restart
request_counts = {}

def rate_limit(limit=5, period=3600):
    """Limit requests to 'limit' per 'period' seconds"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            client_id = request.remote_addr
            
            if client_id not in request_counts:
                request_counts[client_id] = {"count": 0, "reset_time": time.time() + period}
            
            if time.time() > request_counts[client_id]["reset_time"]:
                request_counts[client_id] = {"count": 0, "reset_time": time.time() + period}
                
            if request_counts[client_id]["count"] >= limit:
                remaining_seconds = int(request_counts[client_id]["reset_time"] - time.time())
                return jsonify({
                    "error": f"Rate limit exceeded. Try again in {remaining_seconds} seconds.",
                    "retry_after": remaining_seconds
                }), 429
            
            request_counts[client_id]["count"] += 1
            
            resp = f(*args, **kwargs)
            
            if isinstance(resp, tuple):
                response, status = resp
                if isinstance(response, dict):
                    response = jsonify(response)
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = str(limit - request_counts[client_id]["count"])
                response.headers["X-RateLimit-Reset"] = str(int(request_counts[client_id]["reset_time"]))
                return response, status
            
            resp.headers["X-RateLimit-Limit"] = str(limit)
            resp.headers["X-RateLimit-Remaining"] = str(limit - request_counts[client_id]["count"])
            resp.headers["X-RateLimit-Reset"] = str(int(request_counts[client_id]["reset_time"]))
            return resp
            
        return wrapped
    return decorator

def create_app(test_config=None):
    # Create Flask app
    app = Flask(__name__)
    
    # Load config
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(test_config)
    
    # Register routes directly in app
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')

    @app.route('/generate-quiz', methods=['POST'])
    @rate_limit(limit=5, period=3600)  # 5 requests per hour
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
            logger.exception("Quiz generation failed")
            return jsonify({'error': str(e)}), 500
    
    return app

# For direct execution (development mode)
if __name__ == '__main__':
    import os
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)