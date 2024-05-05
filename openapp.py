from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from uuid import uuid4
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths for directories and files
SAVE_PATH = "./logs/conversations/"
SESSION_PATH = "./logs/current_conversation.json"
FILEPATH = "./logs/test.py"
FILEPATH_CODE = "./logs/function.py"
FILEPATH_TESTCASES = "./logs/testcases.py"
# Functions to ensure directory and files exists
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    print(f"Directory ensured: {directory}")
def ensure_file(filepath):
    directory = os.path.dirname(filepath)
    ensure_dir(directory)  # Ensure the directory exists
    if not os.path.exists(filepath):
        open(filepath, 'a').close()  # Create the file if it does not exist
    print(f"File ensured: {filepath}")
ensure_dir(SAVE_PATH)
ensure_file(SESSION_PATH)
ensure_file(FILEPATH)
ensure_file(FILEPATH_CODE)
ensure_file(FILEPATH_TESTCASES)

# In-memory storage for conversation histories
conversations = {}
def write_code_to_file(answer,filepath):
    with open(filepath, "w") as file:
        file.write("#!/usr/bin/env python3\n")
        file.write(answer)

sytem_prompt_generation = f"""
You are a AI Assistant that writes code in Python, JavaScript and Ruby.
You understand instructions in both English and Japanese.
You Must always think step by step to solve the problem.
"""

@app.post("/generatecode/", response_class=HTMLResponse)
async def generate_code(session_id: str = Form(...), input_text: str = Form(...)):
    print(session_id)
    print(input_text)
    
    if len(input_text) < 5:
        return "<pre class='mb-2'><code class='python'>Error, invalid question</code></pre>"
    
    # Retrieve or create a new conversation history
    if session_id not in conversations:
        conversations[session_id] = [{"role": "system", "content":sytem_prompt_generation}]

    # Append the new user message to the conversation history
    codesnippit_question = f"""
    You should repond with code snippit (function) based on following question - {input_text} \n\n
    Follow the following guidelines for generating the code -
    - If the language of the question is not mentioned, you assume it is Python.
    - Explain the working of the code as a docstring after first line of function name.
    - Only respond with code as plain text without code block syntax around it.
    - Do not include " ```python ``` " around the generated response.
    - Do not provide any additional information after the end of the generated function.
    - do not include running guidelines, testcases and example usage of the function unless explicity specified.
    """
    conversations[session_id].append({"role": "user", "content": codesnippit_question})
    
    # Call chatgpt API 
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversations[session_id]
        )

    # Extract the response text and update conversation history
    answer = completion.choices[0].message.content
    
    conversations[session_id].append({"role": "assistant", "content": answer})
    print(conversations)
    code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
    return code_html

@app.post("/feedbackgeneratecode/", response_class=HTMLResponse)
async def feedback_generate_code(session_id: str = Form(...), input_text: str = Form(...)):
    print(session_id)
    print(input_text)
    
    if len(input_text) < 5:
        return "<pre class='mb-2'><code class='python'>Error, invalid question</code></pre>"
    
    # Retrieve or create a new conversation history
    if session_id not in conversations:
        return f"<pre class='mb-2'><code class='python'>Try Gnerating the code first by defining problem above</code></pre>"
    
    feedbach_question = f"""Now give the new function based on following feedback - {input_text} \n\n
    keep in mind the following guidelines 
        - If the language of the question is not mentioned, you assume it is Python.
        - Explain the working of the code as a docstring after first line of function name.
        - Only respond with code as plain text without code block syntax around it.
        - Do not include " ```python ``` " around the generated response.
        - Do not provide any additional information after the end of the generated function.
        - do not include running guidelines, testcases and example usage of the function unless explicity specified.
    """
    # Append the new user message to the conversation history
    conversations[session_id].append({"role": "user", "content": feedbach_question})
    
    # Call chatgpt API 
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversations[session_id]
        )

    # Extract the response text and update conversation history
    answer = completion.choices[0].message.content
    
    conversations[session_id].append({"role": "assistant", "content": answer})
    print(conversations)
    code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
    return code_html

@app.post("/generatetestcases/", response_class=HTMLResponse)
async def generate_test_cases(session_id: str = Form(...)):
    print(session_id)    
    # Retrieve or create a new conversation history
    if session_id not in conversations:
        return f"<pre class='mb-2'><code class='python'>Try Gnerating the code first by defining problem above</code></pre>"
    
    testcases_prompt = f"""
    Now you must generate testcases to test feasibility of the lastest code above.
    Generate testcases for Functionality Testing, Performace testing and Optimization testing.
        - If you don't know the code, do not generate testcases.
        - Give test testcases for Functionality Testing using unittest or pytest
        - Give code to run performance test using timeit.
        - Give code to run cprofling using cProfile.
        - Give code to run all the above test and assert with expected answer.
    """
    # Append the new user message to the conversation history
    conversations[session_id].append({"role": "user", "content": testcases_prompt})
    
    # Call chatgpt API 
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversations[session_id]
        )

    # Extract the response text and update conversation history
    answer = completion.choices[0].message.content
    
    conversations[session_id].append({"role": "assistant", "content": answer})
    print(conversations)
    code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
    return code_html

@app.post("/feedbacktestcases/", response_class=HTMLResponse)
async def feedback_test_cases(session_id: str = Form(...), input_text: str = Form(...)):
    print(session_id)
    print(input_text)
    
    if len(input_text) < 5:
        return "<pre class='mb-2'><code class='python'>Error, invalid question</code></pre>"
    
    # Retrieve or create a new conversation history
    if session_id not in conversations:
        return f"<pre class='mb-2'><code class='python'>Try Gnerating the code first by defining problem above</code></pre>"
    
    feedbach_question = f"""Now update the testcases based on following feedback feedback - {input_text} \n\n
    you must generate the testcases and keep in mind the following guidelines-
        - If you don't know the code, do not generate testcases.
        - Give test testcases for Functionality Testing using unittest or pytest
        - Give code to run performance test using timeit.
        - Give code to run cprofling using cProfile.
        - Give code to run all the above test and assert with expected answer.
    """
    # Append the new user message to the conversation history
    conversations[session_id].append({"role": "user", "content": feedbach_question})
    
    # Call chatgpt API 
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversations[session_id]
        )

    # Extract the response text and update conversation history
    answer = completion.choices[0].message.content
    
    conversations[session_id].append({"role": "assistant", "content": answer})
    print(conversations)
    code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
    return code_html