import requests

response_main = requests.get("https://desperate-cassandra-michaelbradytuftsgenai-5e8e56d3.koyeb.app/")
print('Web Application Response:\n', response_main.text, '\n\n')

data = {"text":"Tell me about nutrition"}
response_llmproxy = requests.post("https://desperate-cassandra-michaelbradytuftsgenai-5e8e56d3.koyeb.app/query", json=data)
print('LLMProxy Response:\n', response_llmproxy.text)
