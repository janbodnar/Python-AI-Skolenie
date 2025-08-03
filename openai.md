# OpenAI 

The OpenAI Python library is an official SDK that provides seamless access to OpenAI’s REST API  
from any Python 3.8+ application. It’s designed to help developers integrate powerful AI  
capabilities—like text generation, image analysis, and chat interactions—into their own software.  

Built using `httpx` and auto-generated from OpenAI’s OpenAPI specification via the **Stainless** toolchain,   
the library ensures consistent, up-to-date access to all available endpoints and features.  

Since its release, the OpenAI Python library has become the **de facto standard for AI programming in Python**.  
It's widely adopted across industries, research institutions, and open-source communities.  


## Use cases

- Chatbots and virtual assistants
- Text summarization and translation
- Code generation and debugging
- Image generation and editing (via DALL·E)
- Speech-to-text transcription (via Whisper)


## Simple Chat 

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

completion = client.chat.completions.create(
    extra_body={},
    model="z-ai/glm-4.5-air:free",
    messages=[
        {
          "role": "user",
          "content": "Is Pluto a planet?"
        }
    ]
)
print(completion.choices[0].message.content)
```


## Streaming 

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# Enable streaming in the completion request
stream = client.chat.completions.create(
    extra_body={},
    model="z-ai/glm-4.5-air:free",
    messages=[
        {
            "role": "user",
            "content": "Is Pluto a planet?"
        }
    ],
    stream=True  # Enable streaming
)

# Process the stream in real-time
print("Streaming response:")
for chunk in stream:
    # Check if the chunk contains content
    if chunk.choices[0].delta.content is not None:
        # Print the content chunk without a newline
        print(chunk.choices[0].delta.content, end="", flush=True)

# Add a final newline for clean formatting
print()
```
