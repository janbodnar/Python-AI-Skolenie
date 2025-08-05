# LiteLLM


**LiteLLM** is an open-source **Python library** that provides a **unified API** for interacting with  
over **100+ large language model (LLM) providers**. It's designed to make it easy for developers to  
switch between different models—like OpenAI, Anthropic, Hugging Face, VertexAI, and more—without  
rewriting their codebase.

```bash
pip install litellm
```

## Core Capabilities

- **Unified Interface**: Use the same function calls (`completion`, `embedding`, etc.) across all supported providers.
- **Provider-Agnostic**: Switch models by simply changing the model string (e.g., from `openai/gpt-4o` to `huggingface/WizardLM`).
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
