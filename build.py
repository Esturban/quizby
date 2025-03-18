from quizby import  quizby
import datetime
import os
def build_sys_prompt():
    with open(os.getenv("SYSTEM_PROMPT"), "r") as f:
        return f.read()
    

def build_assistant_prompt():
    with open(os.getenv("ASSISTANT_PROMPT"), "r") as f:
        text = f.read()
    with open("data/txt/cdmp-sample.txt", "r") as f:
        quiz_sample = f.read()
    with open("data/txt/dmbok.txt", "r") as f:
        textbook = f.read()
    
    text = text + "\n" \
        + "Here is a sample question from the CDMP exam: \n" \
        + quiz_sample \
        + "\n" \
        + "For complete context about the subject, here's the full book: \n" \
        + textbook
    return text

def build_user_prompt():
    with open(os.getenv("USER_PROMPT"), "r") as f:
        return f.read()

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