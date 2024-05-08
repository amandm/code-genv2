from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from uuid import uuid4
from openai import OpenAI
import subprocess
# import httpx
import json
import re

# httpclient = httpx.Client(verify=False)
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# client = OpenAI(api_key=OPENAI_API_KEY,http_client=httpclient)
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
DIRECTORY = './logs'
FILENAME = 'conversation.json'
os.makedirs(DIRECTORY, exist_ok=True)
SAVE_CONVERSATIONS_PATH = os.path.join(DIRECTORY,FILENAME)

SESSION_PATH = "./logs/current_conversation.json"
FILEPATH = "./logs/end2endcode.py123"

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

ensure_file(SESSION_PATH)
ensure_file(FILEPATH)

def save_conv(dictionay,filepath):
    with open(filepath, 'w') as json_file:
        json.dump(dictionay, json_file)
   
def code_to_testpy(answer,filepath):
    with open(filepath, "w") as file:
        file.write("#!/usr/bin/env python3\n")
        file.write(answer)

def lines_to_testpy(lines,filepath):
    with open(filepath, "w") as file:
        file.write("#!/usr/bin/env python3\n")
        for line in lines:
            file.write(line + "\n")

@app.get("/print_conversations", response_class=HTMLResponse)
async def run_test_cases(session_id: str = Form(...)):
    print(session_id)
    print(conversations[session_id])
    code_html = f"<pre class='mb-2'><code class='python'>{conversations[session_id]}</code></pre>"
    return code_html

# In-memory storage for conversation histories
conversations = {}
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
    
    conversations[session_id].append({"role": "assistant", "content":  f"##codesnippit:\n{answer}"})
    print(conversations)
    code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
    
    save_conv(conversations,SAVE_CONVERSATIONS_PATH)
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
    
    feedback_question = f"""Now give the new function based on following feedback - {input_text} \n\n
    keep in mind the following guidelines 
        - If the language of the question is not mentioned, you assume it is Python.
        - Explain the working of the code as a docstring after first line of function name.
        - Only respond with code as plain text without code block syntax around it.
        - Do not include " ```python ``` " around the generated response.
        - Do not provide any additional information after the end of the generated function.
        - do not include running guidelines, testcases and example usage of the function unless explicity specified.
    """
    # Append the new user message to the conversation history
    conversations[session_id].append({"role": "user", "content": feedback_question})
    
    # Call chatgpt API 
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversations[session_id]
        )

    # Extract the response text and update conversation history
    answer = completion.choices[0].message.content
    
    conversations[session_id].append({"role": "assistant", "content": f"##codesnippit:\n{answer}"})
    print(conversations)
    code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
    
    save_conv(conversations,SAVE_CONVERSATIONS_PATH)
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
        - Only respond with code as plain text without code block syntax around it.
        - Do not include " ```python ``` "  around the generated response.
        - Give testcases for Functionality Testing only with appropriate assert with expected answer.
        """
    #     - If genrating test cases for python code
    #         - Give test testcases for Functionality Testing using unittest or pytest
    #         - Give code to run performance test using timeit.
    #         - Give code to run cprofling using cProfile.
    #     - If genrating test cases for JavaScript or Ruby code, appropriatly give test cases for Functionality Testing and Performance testing.
    #     - Give code to run all the above test and assert with expected answer.
    # """
    # Append the new user message to the conversation history
    conversations[session_id].append({"role": "user", "content": testcases_prompt})
    
    # Call chatgpt API 
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversations[session_id]
        )

    # Extract the response text and update conversation history
    answer = completion.choices[0].message.content
    
    conversations[session_id].append({"role": "assistant", "content": f"##testcases:\n{answer}"})
    print(conversations)
    code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
    
    save_conv(conversations,SAVE_CONVERSATIONS_PATH)
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
    
    feedback_question = f"""Now update the testcases based on following feedback feedback - {input_text} \n\n
    you must generate the testcases and keep in mind the following guidelines-
        - If you don't know the code, do not generate testcases.
        - Only respond with code as plain text without code block syntax around it.
        - Do not include " ```python ``` "  around the generated response.
        - Give testcases for Functionality Testing only with appropriate assert with expected answer.
        """
    #     - If genrating test cases for python code
    #         - Give test testcases for Functionality Testing using unittest or pytest
    #         - Give code to run performance test using timeit.
    #         - Give code to run cprofling using cProfile.
    #     - If genrating test cases for JavaScript or Ruby code, appropriatly give test cases for Functionality Testing and Performance testing.
    #     - Give code to run all the above test and assert with expected answer.
    # """
    # Append the new user message to the conversation history
    conversations[session_id].append({"role": "user", "content": feedback_question})
    
    # Call chatgpt API 
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversations[session_id]
        )

    # Extract the response text and update conversation history
    answer = completion.choices[0].message.content
    
    conversations[session_id].append({"role": "assistant", "content": f"##testcases:\n{answer}"})
    print(conversations)
    code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
    
    save_conv(conversations,SAVE_CONVERSATIONS_PATH)
    return code_html

@app.post("/runtestcases/", response_class=HTMLResponse)
async def run_test_cases(session_id: str = Form(...)):
    print(session_id)
    
    # Retrieve or create a new conversation history
    if session_id not in conversations:
        return f"<pre class='mb-2'><code class='python'>Try Generating the code first by defining problem above</code></pre>"
    
    feedback_question = f"""Now give me a complete end to end python script that can run the latest testcases on updated codesnippit. 
    - The script should print input and output for each testcase.
    - Only respond with code as plain text without code block syntax around it.
    - Do not include " '''python .......''' "  around the generated script."""
    # Append the new user message to the conversation history
    conversations[session_id].append({"role": "user", "content": feedback_question})
    
    # Call chatgpt API 
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversations[session_id]
        )
    # Extract the response text and update conversation history
    answer = completion.choices[0].message.content
    print("generated end2end code", "-"*21)
    print(answer)
    print("-"*42)
    conversations[session_id].append({"role": "assistant", "content": f"""##end-to-end-script: \n{answer}"""})
    # print(conversations)
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "assistant", "content": f"what is the programming language of following code, give me one word answer with each letter capital. \n code: \n{answer}"}]
        )
    code_language = completion.choices[0].message.content
    print("code_language", code_language)
    if re.search("pyt", code_language, re.IGNORECASE):
        code_to_testpy(answer,FILEPATH)
    else :
        return f"<pre class='mb-2'><code class='python'> Progrmming language is not python, hence cannot run code. </code></pre>"
    
    if answer.startswith("'''") or answer.startswith("```"):
        print("The answer starts with '''")
        answer = answer[3:-3]
    else:
        print("The answer does not start with '''")
    
    code_to_testpy(answer,FILEPATH)
    
    print("Content of the file " , "-"*20)
    with open(FILEPATH, 'r') as file:
        content = file.read()
        print(content)
    print("--------------------file " , "-"*20)
    
    mode = 0o755
    os.chmod(FILEPATH, mode)
    process = subprocess.Popen(['python3', FILEPATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    consoleout =  stdout.decode() + "\n" + stderr.decode()
    
    print("stdout:", stdout.decode())
    print("stdout:", stdout)
    print("stderr:", stderr.decode())
    print("stderr:", stderr)
    
    conversations[session_id].append({"role": "user", "content": f"""##logs_and _error:\n{consoleout}"""})
    if len(stderr.decode()) > 2:
        error = f"""Following error happened on running the code - {stderr.decode()}"""
        code_html = f"<pre class='mb-2'><code class='python'>{error}</code></pre>"
        
    else:
        code_html = f"<pre class='mb-2'><code class='python'>Successfully passed all the text cases.\n{consoleout}</code></pre>"
        
    save_conv(conversations,SAVE_CONVERSATIONS_PATH)
    return code_html
     
@app.post("/regenraterun/", response_class=HTMLResponse)
async def regenrate_run(session_id: str = Form(...), input_text: str = Form(...)):
    print(session_id)
    print(input_text)
    
    if len(input_text) < 5:
        return "<pre class='mb-2'><code class='python'>Error, invalid request. give better feedback.</code></pre>"
    
    # Retrieve or create a new conversation history
    if session_id not in conversations:
        return f"<pre class='mb-2'><code class='python'>Try Generating the code first by defining problem above</code></pre>"
    
    lastest_error = conversations[session_id][-1]['content']
    lastest_code = conversations[session_id][-2]['content']
    
    print("-"*50)
    print(lastest_code)
    print("-"*50)
    print(lastest_error)
    print("-"*50)
       
    feedback_question = f"""Now give me a complete final code that solves the ##logs_and _error on ##end-to-end-script.
    Consider following feedback while generating the code:  {input_text}. 
    - The script should print input and output for each testcase.
    - Only respond with code as plain text without code block syntax around it.
    - Do not include " '''python .......''' "  around the generated script.
    """
    # Append the new user message to the conversation history
    conversations[session_id].append({"role": "user", "content": feedback_question})
    # Call chatgpt API 
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversations[session_id]
        )
    answer = completion.choices[0].message.content
    conversations[session_id].append({"role": "assistant", "content": answer})

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "assistant", "content": f"what is the programming language of following code, give me one word answer with each letter capital. \n code: \n{answer}"}]
        )
    code_language = completion.choices[0].message.content
    print("code_language", code_language)
    if re.search("pyt", code_language, re.IGNORECASE):
        code_to_testpy(answer,FILEPATH)
    else :
        return f"<pre class='mb-2'><code class='python'> Progrmming language is not python, hence cannot run code. </code></pre>"
    
    if answer.startswith("'''") or answer.startswith("```"):
        print("The answer starts with '''")
        answer = answer[3:-3]
    else:
        print("The answer does not start with '''")
    
    code_to_testpy(answer,FILEPATH)
    
    print("Content of the file " , "-"*20)
    with open(FILEPATH, 'r') as file:
        content = file.read()
        print(content)
    print("--------------------file " , "-"*20)
    
    mode = 0o755
    os.chmod(FILEPATH, mode)
    process = subprocess.Popen(['python3', FILEPATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    consoleout =  stdout.decode() + "\n" + stderr.decode()
    
    print("stdout:", stdout.decode())
    print("stdout:", stdout)
    print("stderr:", stderr.decode())
    print("stderr:", stderr)
    
    conversations[session_id].append({"role": "user", "content": f"""##logs_and _error:\n{consoleout}"""})
    if len(stderr.decode()) > 2:
        error = f"""Following error happened on running the code - {stderr.decode()}"""
        code_html = f"<pre class='mb-2'><code class='python'>{error}</code></pre>"
        
    else:
        code_html = f"<pre class='mb-2'><code class='python'>Successfully passed all the text cases.\n{consoleout}</code></pre>"
        
    save_conv(conversations,SAVE_CONVERSATIONS_PATH)
    return code_html