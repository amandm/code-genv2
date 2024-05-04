from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import OpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory
import pickle
import datetime

from dotenv import load_dotenv
import os
SAVE_PATH = "./converstaions/"
SESSION_PATH = "./code_and_snippets.pkl"
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
llm = OpenAI(api_key=OPENAI_API_KEY)
system_prompt = "you are a software engineer that writes code in python, javascript and Ruby."
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            system_prompt,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
chain = prompt | llm



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    if len(input_text) < 5:
        return f"<pre class='mb-2'><code class='python'>Error, invalid question</code></pre>"
    answer = chain.invoke(
    {
        "messages": [
            HumanMessage(
                content= generate_wrap + input_text
            ),
        ],
    }
    )
    print("LLM generated response  ")
    print(answer)
    print("-"*30)
    print() 
    chat = [generate_wrap + input_text, answer]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = SAVE_PATH + input_text[:10] + timestamp + ".pkl"
    with open(file_path, 'wb') as file:
        pickle.dump(chat, file)
    with open(SESSION_PATH, 'wb') as file:
        pickle.dump(chat, file)
    chathistory = ChatMessageHistory()
    chathistory.add_user_message(chat[0])
    chathistory.add_ai_message(chat[1])       
    code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
    return code_html

@app.get("/generatetestcases/", response_class=HTMLResponse)
async def generate_testcase():
    try:
        with open(SESSION_PATH, 'rb') as f:
            chat = pickle.load(f)
        print("Generating test cases")
        
        prompt_testcases= "\n\n Now Generate test cases for the mentioned code. Do not give me the code, only give the test cases."
        chathistory = ChatMessageHistory()
        chathistory.add_user_message(chat[0])
        chathistory.add_ai_message(chat[1])
        chathistory.add_user_message(prompt_testcases)
        chat.append(prompt_testcases)
        print(chat)
        answer = chain.invoke(
        {
            "messages": [
                HumanMessage(
                    content= chathistory.messages
                ),
            ],
        }
        )
        print("Test - cases")
        print(answer)
        print("-"*30)
        print() 
        chat.append(answer)
        with open(SESSION_PATH, 'wb') as file:
            pickle.dump(chat, file)   
        code_html = f"<pre class='mb-2'><code class='python'>{answer}</code></pre>"
        return code_html
    except Exception as e:
        return f"Failed to generate test cases: {str(e)}"
    
    
    