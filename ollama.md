# Ollama

## Introduction

**Ollama** is an open-source tool designed to run, manage, and interact with large language  
models (LLMs) locally on your machine. It enables developers, researchers, and hobbyists to  
deploy powerful AI models without relying on cloud-based services, giving complete control  
over data privacy and usage.

Ollama simplifies the complexities of running LLMs by handling model downloads, memory  
management, and inference in an easy-to-use command-line interface. Whether you want to  
experiment with popular models like LLaMA, Mistral, or custom-trained models, Ollama  
provides a seamless experience.

### Why Developers Use Ollama

- **Privacy and Control**: Run models locally without sending data to external servers.  
- **Cost Efficiency**: Avoid recurring cloud API costs for inference.  
- **Experimentation**: Easily try different models and configurations.  
- **Offline Access**: Use AI capabilities without an internet connection.  
- **Customization**: Create and run custom models with Modelfiles.  

### Supported Platforms

Ollama runs on the following operating systems:  

- **macOS** (Apple Silicon and Intel)  
- **Windows** (Windows 10 and later)  
- **Linux** (Ubuntu, Debian, Fedora, and other distributions)  

### Local and Cloud Mode

Ollama is primarily designed for **local execution**, allowing you to run LLMs directly  
on your hardware. However, it also supports deployment in cloud environments when you  
need to scale or share access with a team. The REST API enables integration with any  
application, whether running locally or in the cloud.

---

## Installation

### Prerequisites

Before installing Ollama, ensure your system meets the following requirements:  

- **RAM**: At least 8 GB (16 GB or more recommended for larger models)  
- **Disk Space**: 10 GB minimum for the application and models  
- **GPU (Optional)**: NVIDIA GPU with CUDA support for faster inference  

### macOS Installation

On macOS, you can install Ollama using the official installer or Homebrew.  

**Using the official installer:**  

1. Download the installer from [ollama.com/download](https://ollama.com/download)  
2. Open the downloaded `.dmg` file  
3. Drag Ollama to your Applications folder  
4. Launch Ollama from Applications  

**Using Homebrew:**  

```bash
brew install ollama
```

**Verify the installation:**  

```bash
ollama --version
```

### Windows Installation

On Windows, download and run the official installer.  

1. Download the installer from [ollama.com/download](https://ollama.com/download)  
2. Run the `.exe` installer  
3. Follow the installation wizard  
4. Ollama starts automatically as a background service  

**Verify the installation in PowerShell or Command Prompt:**  

```bash
ollama --version
```

### Linux Installation

On Linux, use the official installation script for a quick setup.  

**Using the installation script:**  

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

This script downloads and installs Ollama, sets up the service, and configures  
the necessary permissions.  

**Start the Ollama service:**  

```bash
systemctl start ollama
```

**Verify the installation:**  

```bash
ollama --version
```

**For GPU support on Linux**, ensure you have the NVIDIA drivers and CUDA toolkit  
installed. Ollama will automatically detect and use your GPU.  

---

## Common Commands

Ollama provides a straightforward CLI for managing models and running inference.  
Below is a table of the most frequently used commands:  

| Command                  | Description                                      |
|--------------------------|--------------------------------------------------|
| `ollama run <model>`     | Run a model interactively                        |
| `ollama list`            | List all available models                        |
| `ollama pull <model>`    | Download a model from Ollama's registry          |
| `ollama ps`              | Show running models and processes                |
| `ollama stop <model>`    | Stop a running model                             |
| `ollama create <model>`  | Create a new model from a Modelfile              |
| `ollama delete <model>`  | Remove a model from local storage                |

### Examples

**Run a model interactively:**  

```bash
ollama run llama2
```

This starts an interactive session where you can type prompts and receive responses.  

**Pull a model from the registry:**  

```bash
ollama pull mistral
```

**List installed models:**  

```bash
ollama list
```

**Delete a model:**  

```bash
ollama delete llama2
```

---

## Python Examples

Ollama exposes a REST API on `http://localhost:11434` that you can use to integrate  
with Python applications. The following examples demonstrate how to interact with  
the API using the `requests` library.  

### REST API Example

This example shows how to send a prompt to a running Ollama model and receive  
a streamed response.  

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama2", "prompt": "Hello there!"}
)

for line in response.iter_lines():
    if line:
        print(line.decode("utf-8"))
```

The `/api/generate` endpoint accepts a JSON payload with the model name and prompt.  
The response is streamed line by line, allowing you to process tokens as they arrive.  
Each line contains a JSON object with the generated text fragment.  

### Non-Streaming Request

If you prefer to receive the complete response at once, you can disable streaming  
by setting `stream` to `false`.  

```python
import requests
import json

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama2",
        "prompt": "What is the capital of France?",
        "stream": False
    }
)

data = response.json()
print(data["response"])
```

This approach is simpler when you do not need real-time output and prefer to work  
with the complete response.  

### Chat Endpoint Example

Ollama also provides a `/api/chat` endpoint for multi-turn conversations. This  
endpoint accepts a list of messages with roles (`system`, `user`, `assistant`).  

```python
import requests
import json

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "phi4-mini",
        "messages": messages,
        "stream": False
    }
)

data = response.json()
print(data["message"]["content"])
```

The chat endpoint maintains context across messages, making it suitable for  
building conversational applications.  

### Listing Available Models

You can query the API to list all locally available models.  

```python
import requests

response = requests.get("http://localhost:11434/api/tags")
data = response.json()

for model in data["models"]:
    print(f"Model: {model['name']}, Size: {model['size']}")
```

This is useful for dynamically selecting models in your application based on  
what is currently installed.  

---

## Python Examples with OpenAI Library

Ollama provides an OpenAI-compatible API endpoint at `http://localhost:11434/v1`.  
This allows you to use the official OpenAI Python library to interact with your  
local Ollama models. This approach provides a familiar interface for developers  
already using the OpenAI SDK.  

Note: The examples below use `llama2` as the model name. Replace this with the  
name of the model you have installed (e.g., `mistral`, `codellama`, `llama3`).  
Run `ollama list` to see your available models.  

### Simple Chat

This example shows how to configure the OpenAI client to connect to your local  
Ollama server and send a basic chat completion request.  

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

response = client.chat.completions.create(
    model="llama2",
    messages=[
        {"role": "user", "content": "Hello there!"}
    ]
)

print(response.choices[0].message.content)
```

The `base_url` points to Ollama's OpenAI-compatible endpoint. The `api_key` can  
be any non-empty string since Ollama does not require authentication for local  
access. The response object follows the OpenAI API structure.  

### Chat with System Prompt

You can include a system message to set the behavior and persona of the model.  
This example demonstrates a multi-turn conversation setup.  

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]

response = client.chat.completions.create(
    model="llama2",
    messages=messages
)

print(response.choices[0].message.content)
```

The system message sets the context for the conversation. You can extend the  
messages list to build multi-turn conversations by appending user and assistant  
messages.  

### Streaming Response

Streaming allows you to receive the model's response token by token as it is  
generated. This provides a more responsive user experience for long outputs.  

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

stream = client.chat.completions.create(
    model="llama2",
    messages=[
        {"role": "user", "content": "Tell me a short story."}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)

print()
```

Setting `stream=True` returns an iterator that yields chunks as they arrive.  
Each chunk contains a delta with the new content. This approach is useful for  
chat interfaces where you want to display text as it is generated.  

### Temperature and Other Parameters

You can adjust generation parameters such as temperature, top_p, and max_tokens  
to control the model's output behavior.  

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

response = client.chat.completions.create(
    model="llama2",
    messages=[
        {"role": "user", "content": "Write a creative poem about the moon."}
    ],
    temperature=0.9,
    max_tokens=200
)

print(response.choices[0].message.content)
```

Temperature controls randomness in the output. Higher values (e.g., 0.9) produce  
more creative responses, while lower values (e.g., 0.2) produce more focused and  
deterministic outputs. The `max_tokens` parameter limits the response length.  

### List Available Models

You can query the available models using the OpenAI client's models endpoint.  
This returns all models that are installed locally in Ollama.  

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

models = client.models.list()

for model in models.data:
    print(f"Model: {model.id}")
```

This is equivalent to running `ollama list` from the command line. You can use  
this to dynamically select models in your application based on what is  
currently installed.  
