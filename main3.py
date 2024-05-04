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
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
llm = OpenAI(api_key=OPENAI_API_KEY)
SAVE_PATH = "./converstaions/"
SESSION_PATH = "./code_and_snippets.json"

template = """You are a AI Assistant that writes code in Python, JavaScript and Ruby.
You understand both English and Japanese.
Your job is to provide  code snippet or generate test cases based on user input.
If you are generating Code snippit, follow the following guidelines-
    - By default, if the language of the question is not mentioned, you assume it is Python.
    - if the language of the question is not mentioned, you assume it is Python.
    - Only respond with code as plain text without code block syntax around it.
    - Do not include " ```python ``` " around the generated response.
    - Do not provide any additional information after the end of the generated function.
    - Explain the working of the code as a docstring after first line of function name.
    - do not include running guidelines, testcases and example usage of the function unless explicity specified.
    
If you are generating testcases, generate only the test cases without providing the code.

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
    print(answer)
    print("-"*100)
    print() 
    extracted_messages = conversation.memory.chat_memory.messages
    ingest_to_db = messages_to_dict(extracted_messages)
    with open(SESSION_PATH, "w") as file:
        json.dump(ingest_to_db,file)
    code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
    return code_html

@app.post("/feedbackgeneratecode/", response_class=HTMLResponse)
async def feedback_generate_code(input_text: str = Form(...)):
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
        answer = reloaded_chain.predict(input="Improve the generated code based on the following feedback - \n" + input_text)
        print("Code genration based on feedback-")
        print(answer)
        print("-"*100)
        print()
        extracted_messages = reloaded_chain.memory.chat_memory.messages
        ingest_to_db = messages_to_dict(extracted_messages) 
        with open(SESSION_PATH, "w") as file:
            json.dump(ingest_to_db,file)
        code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
        return code_html
    
    except Exception as e:
        return f"Failed to improve the code: {str(e)}"

@app.get("/generatetestcases/", response_class=HTMLResponse)
async def generate_testcase():
    try:
        with open(SESSION_PATH, 'r') as file:
            retrieve_from_db = json.load(file)
        print(retrieve_from_db)
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