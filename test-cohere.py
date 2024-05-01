# import cohere 
# co = cohere.Client('ypwZZfVBrmiTXi5hZeFX6tbRaS68BkCzMCeEm6ax') # This is your trial API key
# response = co.chat( 
#   model='command-light',
#   message='<YOUR MESSAGE HERE>',
#   temperature=0.3,
#   chat_history=[{"role": "User", "message": "Can you give me a global market overview of the solar panels?"}, {"role": "Chatbot", "message": "Certainly! Here\'s a brief overview of the global solar panel market: \n\nSolar energy has been gaining immense traction as an environmentally sustainable and reliable energy source across the globe. The demand for solar panels has been increasing year after year, driven by various factors, including governmental incentives, technological advancements, and the growing need for renewable energy. \n\nSolar panels are widely used to generate electricity through the capture and conversion of solar radiation into power. They are majority of the use crystalline silicon as the primary material for the photovoltaic (PV) cells, which makes solar panels cost-effective and efficient. \n\nSolar panels are primarily deployed as a renewable energy source for electricity generation, with the residential, commercial, and industrial sectors being the key end-users. Governments and private organizations have been actively investing in and support solar panel projects to achieve their sustainability goals and meet the energy demands of the growing population. \n\nThe global solar panel market is also characterized by the presence of various players, including local and regional manufacturers, as well as global players. The market is also segmented based on product types, application areas, and region. Additionally, the manufacturing process and installation structures vary across different regions, which leads to variations in pricing. \n\nThe demand for solar panels is influenced by factors such as the increasing awareness of climate change and renewable energy goals, the development and availability of financing options and technologies, and the increasing awareness of the environmental and power benefits of solar energy. \n\nThe global solar panel market is expected to witness significant growth in the coming years, driven by the increasing demand for renewable energy and the positive response to the benefits that solar energy brings."}],
#   prompt_truncation='AUTO',
#   stream=True,
#   connectors=[{"id":"web-search"}]
# ) 
# print(response)

import cohere
import os
from dotenv import load_dotenv
load_dotenv()

api = os.environ.get("COHERE_API_KEY")
co = cohere.Client(api)

for event in co.chat_stream(message="write a small poem about python."):
    if event.event_type == "text-generation":
      print(event.text, end = "",flush=True)
    elif event.event_type == "stream-end":
      print(event.finish_reason)