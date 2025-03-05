from  openai import OpenAI
import os
from dotenv import load_dotenv
import datetime
load_dotenv()

client = OpenAI(
  base_url=os.getenv("BASE_URL"),
  api_key = os.getenv("OR_API_KEY") 
)
def quizby(system_prompt="You're a helpful assistant", assistant_prompt= "You're a helpful assistant", user_prompt = "What is the meaning of life",prefix="quizby"):
    try:
            completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": os.getenv("REFERER"), 
                "X-Title": os.getenv("TITLE"),
            },
            extra_body={},
            model=os.getenv("OR_MODEL"),
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "assistant", "content": assistant_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            )
    except Exception as e:
        print(f"Error: {e}")
    
    target_dir = os.getenv("TARGET_DIR")
    if not os.path.exists(f"{target_dir}"): os.mkdir(f"{target_dir}")
            
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{os.getenv('TARGET_DIR')}/{prefix}_{timestamp}.txt"
    with open(filename, "w") as file:
        file.write(completion.choices[0].message.content)
        file.close()
