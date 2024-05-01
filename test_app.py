import requests

url = 'http://127.0.0.1:8000/generatecode/'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded'
}
data = {
    'input_text': 'sdadassssssssdad'
}

response = requests.post(url, headers=headers, data=data)
print(response.text)