from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

api = os.environ.get("OPENAI_API_KEY")
client = OpenAI(
  api_key=api,
)

system_prompt = f"You are a software developer that writes code in python, Javascript and Ruby.\n" + f"By default if language of question is not mentioned you assume it is python.\n" +f"you provide only code as a output, and expain the working inside the function as doc string."


completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "write a programm to factorize anumber into prime numbers."}
  ]
)

print(completion.choices[0].message.content)