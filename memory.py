from langchain_openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
llm = OpenAI(api_key=OPENAI_API_KEY)

from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

memory = ConversationBufferMemory()
conversation_buf = ConversationChain(
    llm=llm,
    memory=memory)


query1 = "Hi! My name is dave. I do have some questions for you"
query2 = "I live in India. Who is the first president?"
query3 = "What is my name?"
query4 = "Where do I live?"

print("input: ",query1)
a = conversation_buf.predict(input=query1)
print(a)

print("input: ",query2)
a = conversation_buf.predict(input=query2)
print(a)

print("input: ",query3)
a = conversation_buf.predict(input=query3)
print(a)

print("input: ",query4)
a = conversation_buf.predict(input=query4)
print(a)
mem = memory.load_memory_variables({})
print(mem)
memory.clear()
print("--")
print(memory.load_memory_variables({}))
print("--")
print("input: ",query4)

from langchain.memory import ChatMessageHistory
history = ChatMessageHistory()
history.add_messages(mem['history'])
print(history.messages)

# a = conversation_buf.predict(input=query4)
# print(a)