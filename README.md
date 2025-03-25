# Quizby

This is a flask application that generates quizzes for the CDMP based on a quiz topic using LLMs.

## Project Structure

```
quizby/
├── quizby/
│   ├── __init__.py        # Package initialization
│   ├── core.py            # Flask app factory and routes
│   ├── quizby.py          # Core quiz generation logic
│   ├── build.py           # Prompt building functions
│   ├── utils.py           # Utility functions
│   ├── templates/         # HTML templates
│   └── static/            # Static assets and uploads
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── wsgi.py                # WSGI entry point
├── app.py                 # Development entry point
├── Dockerfile             # Docker configuration
├── deploy.sh              # GCP deployment script
├── prompts/               # Prompt templates
├── data/                  # Output data directory
├── assets/                # Reference assets
└── .env                   # Environment variables
```

## Environment Configuration

The application uses environment variables for configuration. Create a `.env` file in the root directory with the following settings:

```
# API settings
BASE_URL=https://openrouter.ai/api/v1
OR_API_KEY=your_openrouter_api_key
OR_MODEL=google/gemini-2.0-pro-exp-02-05:free
REFERER=http://yourdomain.com
TITLE="Your App Title"

# File paths
TARGET_DIR=data/output
SYSTEM_PROMPT=prompts/system/default.txt
ASSISTANT_PROMPT=prompts/assistant/default.txt
USER_PROMPT=prompts/user/default.txt
SAMPLE_FILE=assets/cdmp-sample.txt
BOOK_FILE=assets/cdmp-book.txt

# Deployment settings
PORT=5001
APP_NAME=quizby
GCP_ID=your_gcp_project_id
REGION=your_gcp_region
```

## Installation

To install the required dependencies, run:

```
pip install -r requirements.txt
```

## Usage

1. **Set up your configuration**: 
   - Create a `.env` file with your API keys and settings as shown above
   - The app will load these settings via the config.py file

2. **Run the application locally**: 
   ```
   python app.py
   ```

3. **Docker deployment locally**:
   ```
   docker build -t quizby .
   docker run -p 5001:5001 quizby
   ```

## Google Cloud Platform Deployment

The application includes a deployment script for Google Cloud Platform:

1. **Install Google Cloud SDK** if you haven't already
2. **Authenticate with GCP**:
   ```
   gcloud auth login
   ```
3. **Configure Docker for GCP**:
   ```
   gcloud auth configure-docker
   ```
4. **Update your .env file** with GCP-specific settings:
   - `GCP_ID`: Your Google Cloud project ID
   - `REGION`: Your preferred GCP region (e.g., northamerica-northeast1)
   - `APP_NAME`: Name of your Cloud Run service (default: quizby)
5. **Run the deployment script**:
   ```
   ./deploy.sh
   ```

This will build a Docker image, push it to Google Container Registry, and deploy it to Cloud Run.

## Testing

Run the tests using pytest:

```
pytest
```

## Contributing

Feel free to submit issues or pull requests to improve the project. 

## License

This project is licensed under the MIT License.