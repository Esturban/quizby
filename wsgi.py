from app import create_app

# Used by production WSGI servers
application = create_app()

if __name__ == "__main__":
    # Development server
    application.run(debug=True, host='0.0.0.0')