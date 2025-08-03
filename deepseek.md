# DeepSeek 



## Multi-turn conversation

The DeepSeek /chat/completions API is a "stateless" API, meaning the server does not record the context of  
the user's requests. Therefore, the user must concatenate all previous conversation history and pass it  
to the chat API with each request.

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://api.deepseek.com",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
)

# Round 1
messages = [
    {"role": "user", "content": "What's the highest mountain in the world?"}]
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages
)

messages.append(response.choices[0].message)
# print(f"Messages Round 1: {messages}")

# Round 2
messages.append({"role": "user", "content": "What is the second?"})
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages
)

messages.append(response.choices[0].message)
# print(f"Messages Round 2: {messages}")

for msg in messages:

    if type(msg) is dict:
        print(msg)
    else:
        print(msg.content)
```
