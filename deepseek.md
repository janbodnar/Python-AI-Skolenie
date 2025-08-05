# DeepSeek 


## Simple chat 

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://api.deepseek.com",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Is Pluto a planet?"},
    ],
    stream=False
)

print(response.choices[0].message.content)
```


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

## Function call 

```python
import random
import os
from openai import OpenAI

# --- Step 1: Initialize DeepSeek client ---
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # Make sure this env var is set
    base_url="https://api.deepseek.com"
)

# --- Step 2: Define callable tool for the model ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_random_language",
            "description": "Returns a random language to translate into",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# --- Step 3: Sample input sentence ---
sample_text = "Hello, how are you?"
prompt = f"""Pick a random language using get_random_language and  
translate this sentence into it: '{sample_text}'
"""

# --- Step 4: Initial prompt to model ---
messages = [
    {
        "role": "user",
        "content": prompt
    }
]

# --- Step 5: Function registry (dispatcher) ---


def get_random_language():
    languages = ["Spanish", "Czech", "Hungarian", "French",
                 "German", "Italian", "Slovak", "Polish", "Russian"]
    return random.choice(languages)


function_registry = {
    "get_random_language": get_random_language
}

# --- Step 6: First model call to trigger tool ---
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

tool_calls = response.choices[0].message.tool_calls
if not tool_calls:
    print("No function called. Model said:")
    print(response.choices[0].message.content)
    exit()

# --- Step 7: Extract tool call and execute it ---
tool_call = tool_calls[0]
function_name = tool_call.function.name

# Call corresponding Python function
if function_name in function_registry:
    tool_result = function_registry[function_name]()
else:
    raise ValueError(f"Unknown function: {function_name}")

# --- Step 8: Feed tool call + result back to model ---
messages.append(response.choices[0].message)
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": f'"{tool_result}"'
})

# --- Step 9: Final model call to complete the task ---
final_response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools
)

# --- Output the result ---
print("\n Language selected:", tool_result)
print("Final translation response:")
print(final_response.choices[0].message.content)
```

