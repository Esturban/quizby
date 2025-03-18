import logging
from quizby.core import create_app

logger = logging.getLogger(__name__)


# For direct execution (development mode)
if __name__ == '__main__':
    import os
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)