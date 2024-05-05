from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.schema import messages_from_dict, messages_to_dict
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
import json
from langchain_core.prompts.prompt import PromptTemplate
import datetime
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
llm = OpenAI(api_key=OPENAI_API_KEY, max_tokens=2000,temperature=0)

SAVE_PATH = "./logs/converstaions/"
SESSION_PATH = "./logs/current_conversation.json"
FILEPATH = "./logs/test.py"
FILEPATH_CODE = "./logs/function.py"
FILEPATH_TESTCASES = "./logs/testcases.py"
template = """You are a AI Assistant that writes code in Python, JavaScript and Ruby.
You understand both English and Japanese.
Your job is to provide  code snippet or generate test cases based on user input.
If you are generating Code snippit, follow the following guidelines-
    - If the language of the question is not mentioned, you assume it is Python.
    - Explain the working of the code as a docstring after first line of function name.
    - Only respond with code as plain text without code block syntax around it.
    - Do not include " ```python ``` " around the generated response.
    - Do not provide any additional information after the end of the generated function.
    - do not include running guidelines, testcases and example usage of the function unless explicity specified.
    
If you are generating testcases, you need to give testcases for Functionality Testing, Performace testing and Optimization testing.
    - If you don't know the code, do not generate testcases.
    - Give test testcases for Functionality Testing using unittest or pytest
    - Give code to run performance test using timeit.
    - Give code to run cprofling using cProfile.
    
Below is coversation history between human and you.
Current conversation:
{history}
Human: {input}
AI:
"""

PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generatecode/", response_class=HTMLResponse)
async def generate_code(input_text: str = Form(...)):
    if len(input_text) < 5:
        return f"<pre class='mb-2'><code class='python'>Error, invalid question</code></pre>"
    
    conversation = ConversationChain(
    prompt=PROMPT,
    llm=llm,
    verbose=False,
    memory=ConversationBufferMemory(),
        )
    conversation.memory.clear()
    answer = conversation.predict(input=input_text)
    print("LLM generated response-")
    # print(answer)
    # print() 
    extracted_messages = conversation.memory.chat_memory.messages
    ingest_to_db = messages_to_dict(extracted_messages)
    with open(SESSION_PATH, "w") as file:
        json.dump(ingest_to_db,file)
    code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
    print("writing the function into function.py")
    code_to_testpy(answer,FILEPATH_CODE)
    print("-"*100)
    return code_html

@app.post("/feedbackgeneratecode/", response_class=HTMLResponse)
async def feedback_generate_code(input_text: str = Form(...)):
    try:
        with open(SESSION_PATH, 'r') as file:
            retrieve_from_db = json.load(file)
        # print(retrieve_from_db)
        retrieved_messages = messages_from_dict(retrieve_from_db)
        retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)
        retrieved_memory = ConversationBufferMemory(chat_memory=retrieved_chat_history)
        reloaded_chain = ConversationChain(
            prompt=PROMPT,
            llm=llm,
            verbose=False,
            memory=retrieved_memory
        )
        answer = reloaded_chain.predict(input="Improve the generated code based on the following feedback - \n" + input_text)
        print("Code genration based on feedback-")
        # print(answer)
        # print()
        extracted_messages = reloaded_chain.memory.chat_memory.messages
        ingest_to_db = messages_to_dict(extracted_messages) 
        with open(SESSION_PATH, "w") as file:
            json.dump(ingest_to_db,file)
        code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
        print("writing the feedback function into function.py")
        code_to_testpy(answer,FILEPATH_CODE)
        print("-"*100)
        return code_html
    
    except Exception as e:
        return f"Failed to improve the code: {str(e)}"

@app.get("/generatetestcases/", response_class=HTMLResponse)
async def generate_testcase():
    try:
        with open(SESSION_PATH, 'r') as file:
            retrieve_from_db = json.load(file)
        # print(retrieve_from_db)
        retrieved_messages = messages_from_dict(retrieve_from_db)
        retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)
        retrieved_memory = ConversationBufferMemory(chat_memory=retrieved_chat_history)
        # retrieved_memory.clear()
        reloaded_chain = ConversationChain(
            prompt=PROMPT,
            llm=llm,
            verbose=False,
            memory=retrieved_memory
        )
        answer = reloaded_chain.predict(input="generate test cases for the code.")
        print("Test cases-")
        print(answer)
        print("-"*100)
        print()
        extracted_messages = reloaded_chain.memory.chat_memory.messages
        ingest_to_db = messages_to_dict(extracted_messages) 
        with open(SESSION_PATH, "w") as file:
            json.dump(ingest_to_db,file)
        code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
        print("writing the testcases into testcases.py")
        code_to_testpy(answer,FILEPATH_TESTCASES)
        print("-"*100)
        return code_html
    
    except Exception as e:
        return f"Failed to generate test cases: {str(e)}"
    
@app.post("/feedbackgeneratetestcases/", response_class=HTMLResponse)
async def feedback_generate_testcases(input_text: str = Form(...)):
    try:
        with open(SESSION_PATH, 'r') as file:
            retrieve_from_db = json.load(file)
        print(retrieve_from_db)
        retrieved_messages = messages_from_dict(retrieve_from_db)
        retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)
        retrieved_memory = ConversationBufferMemory(chat_memory=retrieved_chat_history)
        reloaded_chain = ConversationChain(
            prompt=PROMPT,
            llm=llm,
            verbose=False,
            memory=retrieved_memory
        )
        answer = reloaded_chain.predict(input="Generate the testcases based on following feedback - \n" + input_text)
        print("testcase genration based on feedback-")
        print(answer)
        print("-"*100)
        print()
        extracted_messages = reloaded_chain.memory.chat_memory.messages
        ingest_to_db = messages_to_dict(extracted_messages) 
        with open(SESSION_PATH, "w") as file:
            json.dump(ingest_to_db,file)
        code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
        print("writing the improved testcases into testcases.py")
        code_to_testpy(answer,FILEPATH_TESTCASES)
        print("-"*100)
        return code_html
    
    except Exception as e:
        return f"Failed to improve the code: {str(e)}"
    

@app.get("/emptysession/", response_class=HTMLResponse)
async def generate_testcase():
    conversation = ConversationChain(
    prompt=PROMPT,
    llm=llm,
    verbose=False,
    memory=ConversationBufferMemory(),
        )
    conversation.memory.clear()
    with open(SESSION_PATH, "w") as file:
        json.dump({},file)
        
    return f"memory clear, json empty"

@app.get("/runtestcases/", response_class=HTMLResponse)
async def runtestcases():
    try:
        with open(FILEPATH_CODE, 'r') as file:
            code = file.read()
        with open(FILEPATH_TESTCASES, 'r') as file:
            testcases = file.read()    
        
#         prompt_finalcode = f"""Given python function in {code} ans testcses in {testcases}, 
# add 2 files and give me single end to end script, such that it has the main function and its running on the testcases."""
        prompt_finalcode = f"""Give me the python code that achieves the task of combining a function.py -  {code}\n\n and testcases.py {testcases}\n\n into a single python file for functionaloty, optimization and performance test."""
        retrieved_memory = ConversationBufferMemory()
        retrieved_memory.clear()
        reloaded_chain = ConversationChain(
            prompt=PROMPT,
            llm=llm,
            verbose=False,
            memory=retrieved_memory
        )
        answer = reloaded_chain.predict(input=prompt_finalcode)
        code_to_testpy(answer,FILEPATH)
        
        mode = 0o755
        os.chmod(FILEPATH, mode)

        # Run the file with python3 and capture output
        process = subprocess.Popen(['python3', FILEPATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        consoleout =  stdout.decode() + "\n" + stderr.decode()
        # Log the output
        print("stdout:", stdout.decode())
        print("stderr:", stderr.decode())

        return f"<pre class='mb-2'><code class='python'>{consoleout}</code></pre>"
    
    except Exception as e:
        return f"Failed to run the test"
 
def code_to_testpy(answer,filepath):
    with open(filepath, "w") as file:
        file.write("#!/usr/bin/env python3\n")
        file.write(answer)
