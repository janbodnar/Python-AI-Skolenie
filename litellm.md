# LiteLLM


**LiteLLM** is an open-source **Python library** that provides a **unified API** for interacting with  
over **100+ large language model (LLM) providers**. It's designed to make it easy for developers to  
switch between different models—like OpenAI, Anthropic, Hugging Face, VertexAI, and more—without  
rewriting their codebase.

```bash
pip install litellm
```

## Core Capabilities

- **Unified Interface**: Use the same function calls (`completion`, `embedding`, etc.)
  across all supported providers.
- **Provider-Agnostic**: Switch models by simply changing the model string
  (e.g., from `openai/gpt-4o` to `huggingface/WizardLM`).
- **Retry & Fallback Logic**: Automatically handles timeouts and failures by switching to backup models.
- **Cost Tracking & Budgets**: Monitor usage and set spending limits per project.
- **Streaming & Async Support**: Includes support for streaming responses and asynchronous calls.


## Why Use LiteLLM?

- **Simplifies LLM integration** across platforms
- **Reduces vendor lock-in**
- **Speeds up development** with consistent syntax
- **Ideal for experimentation** and scaling across providers

## Environment variables 

It is a standard practice for LiteLLM to automatically looks for provider-specific  
API keys in environment variables based on the model being used. For DeepSeek models,  
it specifically looks for `DEEPSEEK_API_KEY`.



## Basic request via openrouter 

The examples assume the existence of `OPENROUTER_API_KEY` env variable. 

Using `qwen/qwen3-coder:free` model.  

```python
from litellm import completion

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

query = """
Write a Python function that calculates age from a 
date of birth string
"""

response = completion(
  model="openrouter/mistralai/devstral-2512:free",
  messages=[{ "content": query,"role": "user"}]
)

print(response.choices[0].message.content)
```


Using `z-ai/glm-4.5-air:free` model. 

```python
from litellm import completion

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

query = """
Write a Python function that calculates age from a 
date of birth string
"""

response = completion(
  model="openrouter/z-ai/glm-4.5-air:free",
  messages=[{ "content": query,"role": "user"}]
)

print(response.choices[0].message.content)
```


## Calculate cost of request

```python
import litellm

# track_cost_callback

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def track_cost_callback(
    kwargs,                 # kwargs to completion
    completion_response,    # response from completion
    start_time, end_time    # start/end time
):
    # print(kwargs)
    try:
        response_cost = kwargs.get("response_cost", 0)
        # print('completion response:', completion_response)
        print("The cost: ", response_cost)
        print(start_time, end_time)
        print(end_time - start_time, "seconds")
    except Exception as e:
        print("Error in tracking cost:", e)


# set custom callback function
litellm.success_callback = [track_cost_callback]

response = litellm.completion(
    model="deepseek/deepseek-chat",
    messages=[
        {"role": "user", "content": "What is the capital of Slovakia?"}
    ],
)

print(response.choices[0].message.content)
```

## Function call

The script demonstrates function calling with LiteLLM by having an AI model translate  
"Hello, how are you?" into a randomly selected language. It defines a get_random_language  
tool that returns a random language from 9 options, uses DeepSeek via LiteLLM to first  
request this function call, then feeds the result back to the model to complete the  
translation in a two-stage interaction loop.

```python
import random
import litellm

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Define the tool exposed to the model
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

# Sample text to be translated
sample_text = "Hello, how are you?"
prompt = f"""
Pick a random language using get_random_language and 
translate this sentence into it: '{sample_text}'
"""


# Initial user message
messages = [
    {
        "role": "user",
        "content": prompt
    }
]

# Tool function registry
def get_random_language():
    languages = ["Spanish", "Czech", "Hungarian", "French", 
                 "German", "Italian", "Slovak", "Polish", "Russian"]
    return random.choice(languages)

function_registry = {
    "get_random_language": get_random_language
}

# First round: ask model to decide what function to call
response = litellm.completion(
    model="deepseek/deepseek-chat",
    messages=messages,
    tools=tools,
    function_call="auto"
)

# Check if tool was called
tool_calls = response["choices"][0]["message"].get("tool_calls")
if not tool_calls:
    print("No tool was called. Model responded with:")
    print(response["choices"][0]["message"]["content"])
    exit()

tool_call = tool_calls[0]
function_name = tool_call["function"]["name"]
print(f"Model called function: {function_name}")
arguments = tool_call["function"].get("arguments", "{}")

# Run tool if it's registered
if function_name in function_registry:
    tool_result = function_registry[function_name]()
else:
    raise ValueError(f"Unknown function: {function_name}")

# Feed tool call & result back into conversation
messages.append(response["choices"][0]["message"])
messages.append({
    "role": "tool",
    "tool_call_id": tool_call["id"],
    "content": f'"{tool_result}"'  # needs to be a JSON string
})

# Final round: get the model to complete the translation using the tool output
final_response = litellm.completion(
    model="deepseek/deepseek-chat",
    messages=messages,
    tools=tools
)

# Print the model's translated sentence
print("\n Model's Final Translation:")
print(final_response["choices"][0]["message"]["content"])
```

