from langchain_openai import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
llm = OpenAI(api_key=OPENAI_API_KEY)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability.",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

chain = prompt | llm

response = chain.invoke(
    {
        "messages": [
            HumanMessage(
                content="Translate this sentence from English to French: I love programming."
            ),
            AIMessage(content="J'adore la programmation."),
            HumanMessage(content="What did you just say?"),
        ],
    }
)
print(response)












# system_prompt = f"""By default, if the language of the question is not mentioned, you assume it is Python.
# The generated response must follow following guidelines -
# 1. if the language of the question is not mentioned, you assume it is Python.
# """

# template_messages = [
#     SystemMessage(content=system_prompt),
#     HumanMessagePromptTemplate.from_template("{text}"),
# ]
# prompt_template = ChatPromptTemplate.from_messages(template_messages)

# memory = ConversationBufferMemory()
# # memory.load_memory_variables({})

# # chain = prompt_template | llm 

# conversation_chain = ConversationChain(
#     llm=llm,
#     prompt = prompt_template,
#     verbose=False,
#     memory=memory
# )


# def generatecode(question: str):
#     # response = chain.invoke({"text": question})
#     response = conversation_chain.predict(input=question)
#     print(response)
#     # print(type(response))
#     memory.save_context({"input": question}, {"output": response})
    
#     if len(response) <= 1:
#         return {"status" : "reponse not found"}
#     else:
#         return {"answer" : response}
 
# question = "code to factorize a number"   
# op = generatecode(question)
# print(op["answer"])

# print("-"*50)
# memory.load_memory_variables({})

# # op = generatecode("now give me example to run this code on number 156")
# # # print(op["answer"])
# # print(memory.chat_memory)

# # memory.clear()

# # op = generatecode("now give me example to run the code on number 156")
# # print(op["answer"])
# # print(memory.chat_memory)
# # print(op)

# # print(memory.load_memory_variables({}))
# # json_memory = memory.to_json()
# # print(json_memory)

# # filepath = 