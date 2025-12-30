from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='gemini-3-flash-preview', think=True, messages=[
  {
    'role': 'user',
    'content': 'how to exctract keybox.xml from a phone?',
  },
])
print(response['message']['content'])
# or access fields directly from the response object
print(response.message.content)