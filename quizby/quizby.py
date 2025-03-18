from openai import OpenAI
import os
from dotenv import load_dotenv
import datetime
load_dotenv()

client = OpenAI(
  base_url=os.getenv("BASE_URL"),
  api_key=os.getenv("OR_API_KEY") 
)

def quizby(system_prompt="You're a helpful assistant", assistant_prompt="You're a helpful assistant", 
          user_prompt="What is the meaning of life", prefix="quizby", return_content=False):
    """Generate content via OpenAI and optionally save to file"""
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": os.getenv("REFERER", ""), 
                "X-Title": os.getenv("TITLE", ""),
            },
            extra_body={},
            model=os.getenv("OR_MODEL"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": assistant_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
        )
        
        content = completion.choices[0].message.content
        
        # Save to file if target directory is configured
        target_dir = os.getenv("TARGET_DIR")
        if target_dir:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{target_dir}/{prefix}_{timestamp}.txt"
            with open(filename, "w") as file:
                file.write(content)
        
        return content if return_content else None
    
    except Exception as e:
        # Log error but let caller handle it
        print(f"Error in quizby: {e}")
        raise