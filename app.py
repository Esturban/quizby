from flask import Flask, render_template, request, jsonify, current_app
import os
from dotenv import load_dotenv
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

# Load env variables
load_dotenv()

def create_app(config=None):
    """Flask application factory"""
    app = Flask(__name__)
    
    # Configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max upload
    )
    
    # Override config if provided
    if config:
        app.config.from_mapping(config)
        
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Fix for proxies
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    # Register blueprints
    from routes.router import main_bp
    app.register_blueprint(main_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)