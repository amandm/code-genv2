import openai

from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
import os
from dotenv import load_dotenv
load_dotenv()

api = os.environ.get("OPENAI_API_KEY")

openai.api_key = api

chat = ChatOpenAI()
conversation = ConversationChain(
    llm=chat,
    memory=ConversationSummaryBufferMemory(
        llm=ChatOpenAI(), max_token_limit=2048
    ),
    verbose=False,
)

op = conversation.predict(input="what is python?")

print(op)


# from openai import OpenAI

# client = OpenAI()

# stream = client.chat.completions.create(
#     model="gpt-3.5",
#     messages=[{"role": "user", "content": "Say this is a test"}],
#     stream=True,
# )
# for chunk in stream:
#     if chunk.choices[0].delta.content is not None:
#         print(chunk.choices[0].delta.content, end="")
        
        
# messages=[
# {"role": "system", "content": "You are FunnyBot"},
# {"role": "assistant", "content": "relevant: farts exert force"}, # RAG
# {"role": "user", "content": "Do penguin farts propel?"}
# ]        
# SystemMessagePromptTemplate.from_template(
#     f"You are a software developer that writes code in python, Javascript and Ruby"
#     f"By default if language of question is not mentioned you assume it is python"
#     f"you provide only code as a output, and expain the working inside the function as doc string."
# ),
# The `variable_name` here is what must align with memory
  
