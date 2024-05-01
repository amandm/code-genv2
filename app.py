from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

api = os.environ.get("OPENAI_API_KEY")
client = OpenAI(
  api_key=api,
)

system_prompt = f"You are a software developer that writes code in python, Javascript and Ruby.\n" + f"By default if language of question is not mentioned you assume it is python.\n" +f"you provide only code as a output, and expain the working inside the function as doc string."


@app.post("/generatecode/", response_class=HTMLResponse)
async def generate_code(input_text: str = Form(...)):
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_text}
            ]
        )

    # "write a programm to factorize anumber into prime numbers."
    
    # Assuming input_text is Python code, we wrap it in HTML tags for syntax highlighting
    code_html = f"<pre class='mb-2'><code class='python'>{completion.choices[0].message.content}</code></pre>"
    return code_html


# from fastapi import FastAPI, Form
# from fastapi.responses import JSONResponse

# app = FastAPI()
# from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Adjust this in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# # <<Implement your APIs here>>
# @app.post("/generatecode/")
# async def generate_code(input_text: str = Form(...)):
#     # Process the input_text here (for demonstration, we just echo it)
#     op = f"""{input_text} is generated"""
#     processed_text = f"Processed: {op} "
#     print(processed_text)
#     return JSONResponse(content={"result": processed_text})
