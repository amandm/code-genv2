from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api = os.environ.get("OPENAI_API_KEY")
client = OpenAI(
  api_key=api,
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

system_prompt = f"""You are a software developer that writes code in python, Javascript and Ruby."""

# Return the reponse in json formt which has following keys-
#     language : programatic language of genegrated code
#     Gnerated_code : the generated code itself
#3. first line should only idicate the languae of generated code.

generate_wrap = f"""Generate the code response based on the below question.
By default, if the language of the question is not mentioned, you assume it is Python.
The generated code must follow following guidelines -
1. if the language of the question is not mentioned, you assume it is Python.
2. Only respond with code as plain text without code block syntax around it.
3. Do not include " ```python ``` " around the generated response.
4. Do not provide any additional information after the end of the generated function.
5. Explain the working of the code as a docstring after first line of function name.
6. do not include running guidelines, testcases and example usage of the function unless explicity specified.

Question -  
"""

@app.post("/generatecode/", response_class=HTMLResponse)
async def generate_code(input_text: str = Form(...)):
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": generate_wrap + input_text}
            ]
        )
    op = completion.choices[0].message.content
    
    print("LLM generated response  ")
    print(op)
    print("-"*30)
    print()        
    code_html = f"<pre class='mb-2'><code class='python'>{op}</code></pre>"
    return code_html
