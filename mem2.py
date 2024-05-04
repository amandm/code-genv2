from langchain_openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
llm = OpenAI(api_key=OPENAI_API_KEY)

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
system_prompt = "you are a software engineer that writes code in python"
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
generate_code = "code to factorize a number."
answer = chain.invoke(
    {
        "messages": [
            HumanMessage(
                content= generate_code
            ),
        ],
    }
)

# print(answer)

chat = [generate_code,answer]
from langchain.memory import ChatMessageHistory
chathistory = ChatMessageHistory()
chathistory.add_user_message(chat[0])
chathistory.add_ai_message(chat[1])

print(chathistory.messages)

generate_test_cases = "Generate test cases for above code."

chathistory.add_user_message(generate_test_cases)

response = chain.invoke(
    {
        "messages": chathistory.messages,
    }
)
print(response)

# print(chathistory)