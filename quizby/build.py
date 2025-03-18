from quizby import quizby
import datetime
import os

def safe_read_file(env_var):
    """Read file with path resolution fallback"""
    file_path = os.getenv(env_var)
    if not file_path:
        return f"Error: Environment variable {env_var} not set"
    
    # Try direct path first
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            return f.read()
    
    # Try relative to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    alt_path = os.path.join(script_dir, file_path)
    if os.path.isfile(alt_path):
        with open(alt_path, "r") as f:
            return f.read()
    
    # Try relative to project root
    project_root = os.path.dirname(script_dir)
    alt_path = os.path.join(project_root, file_path)
    if os.path.isfile(alt_path):
        with open(alt_path, "r") as f:
            return f.read()
            
    return f"Error: Could not find file {file_path}"

def build_sys_prompt():
    return safe_read_file("SYSTEM_PROMPT")

def build_assistant_prompt():
    text = safe_read_file("ASSISTANT_PROMPT")
    quiz_sample = safe_read_file("SAMPLE_FILE")
    textbook = safe_read_file("BOOK_FILE")
    
    return text + "\n" \
        + "Here is a sample question from the CDMP exam: \n" \
        + quiz_sample \
        + "\n" \
        + "For complete context about the subject, here's the full book: \n" \
        + textbook

def build_user_prompt():
    return safe_read_file("USER_PROMPT")

def main(return_content=False):
    system_prompt = build_sys_prompt()
    assistant_prompt = build_assistant_prompt()
    user_prompt = build_user_prompt()
    return quizby(system_prompt, assistant_prompt, user_prompt, return_content=return_content)

if __name__ == "__main__":
    start_time = datetime.datetime.now()
    main()
    end_time = datetime.datetime.now()
    print(f"Time taken: {end_time - start_time}")