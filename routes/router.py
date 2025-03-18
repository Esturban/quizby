from flask import Blueprint, render_template, request, jsonify, current_app
import datetime
import logging
from quizby.quizby import quizby
from quizby.build import build_sys_prompt, build_assistant_prompt, build_user_prompt

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@main_bp.route('/generate-quiz', methods=['POST'])
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