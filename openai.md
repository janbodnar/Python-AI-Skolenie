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

A minimal “hello world” chat that sends one user message to a model via OpenRouter and prints  
the reply. Use this to verify your environment (API key, base_url) and confirm the client  
returns a response.  

Key bits: initialize OpenAI with OpenRouter `base_url`, provide a messages list, and  
read `choices[0].message.content`.

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

Demonstrates token-by-token streaming so you can display the model’s response in real time.  
Set stream=True and iterate over the server-sent events, printing `chunk.choices[0].delta.content`  
as it arrives.

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

## Streaming with Gradio

```python
import os
import json
import typing as t
import httpx
import gradio as gr

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
DEFAULT_SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful AI assistant.")
# Default network timeout in seconds (user requested 30s)
DEFAULT_TIMEOUT_S = float(os.getenv("OPENROUTER_TIMEOUT_S", "30"))


# This example demonstrates how to set up a Gradio chat interface
# that interacts with OpenRouter's chat completions API.
# It includes a simple mock backend for local testing without an API key.


def _headers() -> dict:
    if not OPENROUTER_API_KEY:
        return {}
    # OpenRouter recommends setting HTTP Referer + Title for attribution
    site_url = os.getenv("SITE_URL", "http://localhost")
    app_name = os.getenv("APP_NAME", "Gradio OpenRouter Chat")
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": site_url,
        "X-Title": app_name,
    }


async def fetch_models() -> t.List[str]:
    """
    Fetch the available model IDs from OpenRouter.
    Returns a list of model identifiers.
    """
    if not OPENROUTER_API_KEY:
        # No key: return a tiny demo list with a mock backend
        return ["mock/echo", "deepseek/deepseek-chat", "openai/gpt-4o-mini"]
    url = f"{OPENROUTER_BASE_URL}/models"
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_S) as client:
        r = await client.get(url, headers=_headers())
        r.raise_for_status()
        data = r.json()
    models = []
    for m in data.get("data", []):
        mid = m.get("id")
        if isinstance(mid, str):
            models.append(mid)
    # Sort models alphabetically for easier selection
    return sorted(models)


async def call_openrouter(
    model: str,
    messages: t.List[dict],
    temperature: float = 0.7,
    stream: bool = False,
) -> str:
    """
    Call OpenRouter chat completions. If model == 'mock/echo', returns a simple echo.
    """
    if model == "mock/echo" or not OPENROUTER_API_KEY:
        # Simple deterministic mock for local testing
        user_last = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return f"[mock echo] {user_last}"

    url = f"{OPENROUTER_BASE_URL}/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": False,  # Gradio simple response; you can extend to streaming later
    }
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_S) as client:
        r = await client.post(url, headers=_headers(), json=payload)
        r.raise_for_status()
        data = r.json()

    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return json.dumps(data, indent=2)


def _history_to_messages(
    history: t.Union[t.List[t.Tuple[str, str]], t.List[dict]],
    system_prompt: str,
) -> t.List[dict]:
    """
    Convert Gradio Chatbot history to OpenRouter messages format with a system prompt.

    Supports both legacy tuple history [(user, assistant), ...] and
    Chatbot(type="messages") history [{"role": "...", "content": ...}, ...].
    """
    messages: t.List[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if not history:
        return messages

    # Detect format: dict messages vs tuple pairs
    if isinstance(history[0], dict):
        # Already role/content; validate and append
        for m in history:
            role = m.get("role")
            content = m.get("content")
            if role in ("user", "assistant", "system"):
                messages.append({"role": role, "content": content})
            else:
                # Skip unknown roles to be safe
                continue
    else:
        # Expect iterable of (user, assistant) pairs
        for item in history:
            if isinstance(item, (list, tuple)):
                if len(item) == 2:
                    user_msg, assistant_msg = item
                    if user_msg:
                        messages.append({"role": "user", "content": user_msg})
                    if assistant_msg:
                        messages.append({"role": "assistant", "content": assistant_msg})
                else:
                    # Ignore malformed tuple lengths
                    continue
            else:
                # Ignore unsupported entries
                continue
    return messages


async def respond_fn(
    message: str,
    history: t.List[t.Tuple[str, str]],
    model: str,
    system_prompt: str,
    temperature: float,
) -> str:
    """
    Gradio ChatInterface respond function.
    """
    messages = _history_to_messages(history, system_prompt or DEFAULT_SYSTEM_PROMPT)
    messages.append({"role": "user", "content": message})
    reply = await call_openrouter(model=model, messages=messages, temperature=temperature, stream=False)
    return reply


with gr.Blocks(title="OpenRouter Gradio Chat", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# OpenRouter Chat")
    with gr.Row():
        with gr.Column(scale=3):
            model_dropdown = gr.Dropdown(
                label="Model (loaded from OpenRouter)",
                choices=["Loading..."],
                value="Loading...",
                interactive=True,
            )
            temperature = gr.Slider(
                minimum=0.0,
                maximum=2.0,
                step=0.1,
                value=0.7,
                label="Temperature",
            )
        with gr.Column(scale=4):
            system_prompt_box = gr.Textbox(
                label="System Prompt",
                value=DEFAULT_SYSTEM_PROMPT,
                lines=3,
                placeholder="You are a helpful AI assistant.",
            )

    chat = gr.Chatbot(
        label="Conversation",
        height=500,
        type="messages",
    )

    # Custom aligned input row with Send and Terminate buttons
    # Using compact row to keep controls on one line; scales ensure alignment.
    with gr.Row(variant="compact"):
        user_input = gr.Textbox(
            placeholder="Ask me anything...",
            lines=2,
            scale=8,
            show_label=False,
            container=True,
        )
        with gr.Column(scale=1):
            send_btn = gr.Button("Send", variant="primary")
        with gr.Column(scale=1):
            stop_btn = gr.Button("Terminate", variant="stop")

    # Wire up events: Enter on textbox or Send button triggers respond_fn.
    # Gradio Chatbot(type="messages") requires returning a list of {"role","content"} dicts.
    async def _respond(message, history, model, system_prompt, temperature):
        # history is a list of (user, assistant) tuples from Chatbot
        # Build role/content messages including system
        messages = _history_to_messages(history or [], system_prompt or DEFAULT_SYSTEM_PROMPT)
        if message and message.strip():
            messages.append({"role": "user", "content": message})
        # Call model and append assistant reply
        reply = await call_openrouter(model=model, messages=messages, temperature=temperature, stream=False)
        messages.append({"role": "assistant", "content": reply})
        # Return full messages list to satisfy Chatbot(type="messages")
        return messages

    send_event = send_btn.click(
        _respond,
        inputs=[user_input, chat, model_dropdown, system_prompt_box, temperature],
        outputs=chat,
        queue=True,
        api_name=False,
    )
    # Submit on Enter in textbox
    submit_event = user_input.submit(
        _respond,
        inputs=[user_input, chat, model_dropdown, system_prompt_box, temperature],
        outputs=chat,
        queue=True,
        api_name=False,
    )

    # Terminate button cancels any running jobs and re-enables inputs
    def _noop():
        return gr.update()

    stop_btn.click(
        _noop,
        None,
        None,
        cancels=[send_event, submit_event],
    )

    async def load_models():
        models = await fetch_models()
        # Default to a reasonable commonly-available model if present
        default = "openai/gpt-4o-mini" if "openai/gpt-4o-mini" in models else models[0] if models else "mock/echo"
        return gr.Dropdown(choices=models or ["mock/echo"], value=default)

    demo.load(load_models, inputs=None, outputs=model_dropdown)

if __name__ == "__main__":
    # 0.0.0.0 allows LAN access; change as preferred
    # Gradio 4.x: queue() no longer supports concurrency_count; use default queue.
    # Set share via env var if desired; otherwise local-only.
    share = os.getenv("GRADIO_SHARE", "false").lower() in ("1", "true", "yes")
    demo.queue().launch(server_name="localhost", server_port=int(os.getenv("PORT", "7860")), share=share)
```

## Using DeepSeek 

Shows how to target DeepSeek’s native API with the OpenAI-compatible SDK.  
Configure base_url to `https://api.deepseek.com` and use the model `deepseek-chat` with your `DEEPSEEK_API_KEY`.  
This example performs a non-streaming chat completion with a simple system+user prompt.  

```python
# Please install OpenAI SDK first: `pip install openai`

from openai import OpenAI
import os

# DEEP_SEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
# print(DEEP_SEEK_API_KEY)

# exit

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

## Function call/tool call

This example demonstrates how to use the OpenRouter-compatible OpenAI SDK  
to call a model with function calling capabilities, specifically DeepSeek's  
chat model.

```python
import random
import os
from openai import OpenAI


# Initialize DeepSeek client
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # Make sure this env var is set
    base_url="https://api.deepseek.com"
)

# Define callable tool for the model
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

# Initial prompt to model

sample_text = "Hello, how are you?"

prompt = f"""Pick a random language using get_random_language and 
translate this sentence into it: '{sample_text}'
"""

messages = [
    {
        "role": "user",
        "content": prompt
    }
]

# Function registry (dispatcher) ---
def get_random_language():
    languages = ["Spanish", "Czech", "Hungarian", "French", 
                 "German", "Italian", "Slovak", "Polish", "Russian"]
    return random.choice(languages)

function_registry = {
    "get_random_language": get_random_language
}

# First model call to trigger tool
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

# Extract tool call and execute it
tool_call = tool_calls[0]
function_name = tool_call.function.name

# Call corresponding Python function
if function_name in function_registry:
    tool_result = function_registry[function_name]()
else:
    raise ValueError(f"Unknown function: {function_name}")

# Feed tool call + result back to model
messages.append(response.choices[0].message)
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": f'"{tool_result}"'
})

# Final model call to complete the task
final_response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools
)

# Output the result
print("\n Language selected:", tool_result)
print("Final translation response:")
print(final_response.choices[0].message.content)
```

## Temperature with tool call

The next example demonstrates how to use OpenAI's function calling capabilities  
to create a CLI app that fetches the current temperature for a given city using  
the Open-Meteo API. The app uses natural language processing to extract the city  
name from user queries and provides structured output.  


```python
"""
Temperature CLI App using OpenAI Tools API (DeepSeek)
This app determines the temperature for any chosen city using Open-Meteo API
"""

import json
import requests
import os
import sys
import openai

# Configure OpenAI client for DeepSeek
deepseek_client = openai.OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

# Function to get coordinates for a city using Open-Meteo Geocoding API
def geocode_city(city_name):
    """Get latitude and longitude for a given city name."""
    print('geocode_city')
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            return {
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "name": result.get("name", city_name),
                "country": result.get("country", "")
            }
        else:
            raise ValueError(f"City '{city_name}' not found")

    except Exception as e:
        raise Exception("Error getting temperature") from e

# Function to get weather from Open-Meteo API
def fetch_current_weather(latitude, longitude):
    """Get current weather for given coordinates."""
    print('fetch_current_weather')
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true",
            "temperature_unit": "celsius"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return {
            "temperature": data["current_weather"]["temperature"],
            "windspeed": data["current_weather"]["windspeed"],
            "winddirection": data["current_weather"]["winddirection"],
            "weathercode": data["current_weather"]["weathercode"],
            "time": data["current_weather"]["time"]
        }

    except Exception as e:
        raise Exception("Error getting temperature") from e

# Define tool schema for Tools API
WEATHER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_city_weather",
            "description": "Get the current weather for a specific city. Extract the city name from natural language queries about weather, temperature, or climate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_name": {
                        "type": "string",
                        "description": "The name of the city to get weather for. Extract this from natural language queries like 'What's the weather in Paris?' or 'How hot is it in Tokyo?'"
                    }
                },
                "required": ["city_name"]
            }
        }
    }
]

# Combined function that uses both geocoding and weather APIs
def fetch_city_weather(city_name):
    """Get weather for a city using city name."""
    try:
        # Get coordinates
        city_info = geocode_city(city_name)

        # Get weather
        weather_data = fetch_current_weather(city_info["latitude"], city_info["longitude"])

        # Combine results
        return {
            "city": city_info["name"],
            "country": city_info["country"],
            "coordinates": {
                "latitude": city_info["latitude"],
                "longitude": city_info["longitude"]
            },
            "temperature": weather_data["temperature"],
            "windspeed": weather_data["windspeed"],
            "winddirection": weather_data["winddirection"],
            "weathercode": weather_data["weathercode"],
            "time": weather_data["time"]
        }

    except Exception as e:
        raise Exception("Error getting city weather") from e

# Process natural language queries using Tools API
def resolve_weather_query(query):
    """Process natural language query using Tools API."""
    print('resolve_weather_query')
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a weather assistant. When the user asks about weather or temperature, "
                    "identify the most likely city name and call the function fetch_city_weather "
                    "with parameter {\"city_name\": \"...\"}. Do not answer directly."
                ),
            },
            {"role": "user", "content": query},
        ]

        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=WEATHER_TOOLS,
            tool_choice={"type": "function", "function": {"name": "fetch_city_weather"}}
        )

        msg = response.choices[0].message

        # Expect a tool call
        if getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                if getattr(tc, "type", "") == "function" and getattr(tc, "function", None):
                    fn = tc.function
                    if fn.name == "fetch_city_weather":
                        args = json.loads(fn.arguments or "{}")
                        city_name = args.get("city_name")
                        if city_name:
                            return fetch_city_weather(city_name)

        raise ValueError("No tool call produced or city name not found")

    except Exception as e:
        raise Exception("Error processing query") from e

# Weather code descriptions
WEATHER_CODE_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

def describe_weather_code(code):
    """Get weather description from weather code."""
    return WEATHER_CODE_DESCRIPTIONS.get(code, "Unknown")

def format_weather_report(data):
    """Format the weather data for display."""
    weather_desc = describe_weather_code(data["weathercode"])

    output = f"""
╔══════════════════════════════════════════════════════════════╗
║                    WEATHER REPORT                            ║
╠══════════════════════════════════════════════════════════════╣
║ City: {data['city']}, {data['country']}
║ Coordinates: {data['coordinates']['latitude']:.2f}°N, {data['coordinates']['longitude']:.2f}°E
║ Time: {data['time']}
║ Temperature: {data['temperature']}°C
║ Weather: {weather_desc}
║ Wind: {data['windspeed']} km/h at {data['winddirection']}°
╚══════════════════════════════════════════════════════════════╝
"""
    return output

def main():

    print("Temperature CLI App with OpenAI DeepSeek (Tools API)")
    print("=" * 50)

    # Check if OpenAI API key is set
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("Error: DEEPSEEK_API_KEY environment variable not set")
        print("Please set your OpenAI API key: export DEEPSEEK_API_KEY='your-key-here'")
        sys.exit(1)

    # Get user input
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter city name or weather query: ").strip()

    if not query:
        print("Error: No input provided")
        sys.exit(1)

    try:
        print(f"\nProcessing query: '{query}'...")

        # Process the query
        result = resolve_weather_query(query)

        # Display results
        print(format_weather_report(result))

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Temperature without tool call

The following example determines the weather in a city without a tool call. We request  
the model to return a JSON output and pass it directly to `fetch_city_weather`. 

```python
"""
Temperature CLI App using OpenAI DeepSeek without Function Calling
This app determines the temperature for any chosen city using Open-Meteo API
"""

import json
import requests
import os
import sys
import openai

# Configure OpenAI client for DeepSeek
deepseek_client = openai.OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


# Function to get coordinates for a city using Open-Meteo Geocoding API
def geocode_city(city_name):
    """Get latitude and longitude for a given city name."""
    print('geocode_city')
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            return {
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "name": result.get("name", city_name),
                "country": result.get("country", "")
            }
        else:
            raise ValueError(f"City '{city_name}' not found")

    except Exception as e:
        raise Exception("Error getting temperature") from e


# Function to get weather from Open-Meteo API
def fetch_current_weather(latitude, longitude):
    """Get current weather for given coordinates."""
    print('fetch_current_weather')
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true",
            "temperature_unit": "celsius"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return {
            "temperature": data["current_weather"]["temperature"],
            "windspeed": data["current_weather"]["windspeed"],
            "winddirection": data["current_weather"]["winddirection"],
            "weathercode": data["current_weather"]["weathercode"],
            "time": data["current_weather"]["time"]
        }

    except Exception as e:
        raise Exception(f"Error getting temperature") from e


# Combined function that uses both geocoding and weather APIs
def fetch_city_weather(city_name):
    """Get weather for a city using city name."""
    print('fetch_city_weather')
    try:
        # Get coordinates
        city_info = geocode_city(city_name)

        # Get weather
        weather_data = fetch_current_weather(
            city_info["latitude"], city_info["longitude"])

        # Combine results
        return {
            "city": city_info["name"],
            "country": city_info["country"],
            "coordinates": {
                "latitude": city_info["latitude"],
                "longitude": city_info["longitude"]
            },
            "temperature": weather_data["temperature"],
            "windspeed": weather_data["windspeed"],
            "winddirection": weather_data["winddirection"],
            "weathercode": weather_data["weathercode"],
            "time": weather_data["time"]
        }

    except Exception as e:
        raise Exception(f"Error getting city weather") from e

# Function to process natural language queries using OpenAI


def resolve_weather_query(query):
    """Process natural language query using OpenAI."""
    print('resolve_weather_query')
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a weather assistant. Extract the city name from the user's query about weather or temperature. "
                    "Respond ONLY with JSON in this format: {\"city_name\": \"city_name_here\"}. "
                    "If no city is found, respond with {\"city_name\": null}."
                ),
            },
            {"role": "user", "content": query},
        ]

        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0
        )

        msg = response.choices[0].message

        content = msg.content or ""
        data = json.loads(content)
        city_name = data.get("city_name")

        if city_name:
            return fetch_city_weather(city_name)

        raise ValueError("Could not determine city from query")

    except Exception as e:
        print(e)

        raise Exception(f"Error processing query") from e


# Weather code descriptions
WEATHER_CODE_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}


def describe_weather_code(code):
    """Get weather description from weather code."""
    return WEATHER_CODE_DESCRIPTIONS.get(code, "Unknown")


def format_weather_report(data):
    """Format the weather data for display."""
    weather_desc = describe_weather_code(data["weathercode"])

    output = f"""
╔══════════════════════════════════════════════════════════════╗
║                    WEATHER REPORT                            ║
╠══════════════════════════════════════════════════════════════╣
║ City: {data['city']}, {data['country']}
║ Coordinates: {data['coordinates']['latitude']:.2f}°N, {data['coordinates']['longitude']:.2f}°E
║ Time: {data['time']}
║ Temperature: {data['temperature']}°C
║ Weather: {weather_desc}
║ Wind: {data['windspeed']} km/h at {data['winddirection']}°
╚══════════════════════════════════════════════════════════════╝
"""
    return output


def main():

    print("Temperature CLI App with OpenAI DeepSeek")
    print("=" * 50)

    # Check if OpenAI API key is set
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("Error: DEEPSEEK_API_KEY environment variable not set")
        print("Please set your OpenAI API key: export DEEPSEEK_API_KEY='your-key-here'")
        sys.exit(1)

    # Get user input
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter city name or weather query: ").strip()

    if not query:
        print("Error: No input provided")
        sys.exit(1)

    try:
        print(f"\nProcessing query: '{query}'...")

        # Process the query
        result = resolve_weather_query(query)

        # Display results
        print(format_weather_report(result))

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```



## System prompts and persona swapping (OpenRouter + OpenAI SDK compatible)

This example demonstrates how swapping only the system prompt changes the  
model's persona and behavior, while keeping user inputs the same. It also shows  
optional multi-turn memory while changing personas.  

Prerequisites:
- Environment variable OPENROUTER_API_KEY set  
- openai Python package installed (pip install openai)  
- Using OpenRouter-compatible OpenAI client configuration:  
  - base_url="https://openrouter.ai/api/v1"  
  - api_key=os.environ["OPENROUTER_API_KEY"]  


System prompts are a powerful way to set the model's persona, tone, and  
behavior. By changing the system prompt, you can make the model act like a   
different character or expert, even if the user input remains the same.  

Persona swapping is useful for:  
- Creating multi-character chatbots  
- Adapting the model's tone for different audiences  
- Testing how the model responds to different personas  


## Single-turn: swap personas by system prompt

Single-turn examples show how to change the system prompt to swap personas   
for a single user message. The system prompt at index 0 is the only thing that    
changes; the user message remains the same. This allows you to see how the model   
responds differently based on the system persona.    

```python
# system_persona_examples.py
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

MODEL = "z-ai/glm-4.5-air:free"

def run_chat(system_prompt: str, user_message: str) -> str:
    """Run a single-turn chat with a given system persona."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return resp.choices[0].message.content

def persona_swapping_single_turn():
    user_question = "Explain recursion to a 10-year-old in 2-3 sentences."

    # Persona A: Friendly teacher
    system_a = (
        "You are a friendly grade-school teacher. "
        "Use simple language, warmth, and 2-3 short sentences."
    )
    answer_a = run_chat(system_a, user_question)
    print("\n--- Persona A (Friendly teacher) ---\n" + answer_a)

    # Persona B: Concise senior software engineer
    system_b = (
        "You are a concise senior software engineer. "
        "Be precise, use minimal words, and avoid fluff."
    )
    answer_b = run_chat(system_b, user_question)
    print("\n--- Persona B (Senior engineer) ---\n" + answer_b)

if __name__ == "__main__":
    persona_swapping_single_turn()
```

Run:
```
python system_persona_examples.py
```

Expected behavior: The two answers differ in tone and style, even though the user  
message is identical. Only the system role changed.  

## Multi-turn: preserve memory while swapping personas

The multi-turn example shows how to maintain conversation history while swapping  
personas. The system message at index 0 is replaced to change the persona for  
the next turn, while keeping the conversation context intact.  


```python
# system_persona_examples.py
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

MODEL = "z-ai/glm-4.5-air:free"

def run_chat(system_prompt: str, user_message: str) -> str:
    """Run a single-turn chat with a given system persona."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return resp.choices[0].message.content

# system_persona_examples.py (continued)
def persona_swapping_multi_turn():
    # Start with Persona A and build context
    system_a = (
        "You are a friendly grade-school teacher. "
        "Use simple language, warmth, and 2-3 short sentences."
    )

    # Conversation history with Persona A
    history = [
        {"role": "system", "content": system_a},
        {"role": "user", "content": "I'm learning Python. What is a function?"},
    ]
    resp1 = client.chat.completions.create(model=MODEL, messages=history)
    print("\n[A1 - Teacher]\n" + resp1.choices[0].message.content)
    history.append(resp1.choices[0].message)

    # Continue with Persona A for follow-up
    history.append({"role": "user", "content": "Can you give a very short example?"})
    resp2 = client.chat.completions.create(model=MODEL, messages=history)
    print("\n[A2 - Teacher]\n" + resp2.choices[0].message.content)
    history.append(resp2.choices[0].message)

    # Swap to Persona B but preserve history context;
    # IMPORTANT: replace the last system message to steer new turns.
    system_b = (
        "You are a concise senior software engineer. "
        "Be precise and avoid fluff. Keep answers tight."
    )
    # Replace the initial system message with Persona B for the next turn:
    history[0] = {"role": "system", "content": system_b}

    # Ask another follow-up; model retains previous conversation content
    history.append({"role": "user", "content": "Optimize the example for clarity."})
    resp3 = client.chat.completions.create(model=MODEL, messages=history)
    print("\n[B1 - Senior engineer]\n" + resp3.choices[0].message.content)

if __name__ == "__main__":
    persona_swapping_multi_turn()
```

Notes:
- In multi-turn flows, the conversation "memory" is the prior messages you send  
  back each time. Swapping personas is done by changing the system message at  
  index 0 while keeping the rest of the history.  
- You can insert or prepend a new system message for the next turn; most APIs  
  use the first system message as the active instruction.  

## Minimal persona system prompts

- Helpful tutor:
  - "You are a friendly tutor. Use simple language, empathy, and short
    sentences."
- Product manager:
  - "You are a pragmatic product manager. Focus on user impact, trade-offs, and
    prioritization."
- Senior engineer:
  - "You are a concise senior software engineer. Be precise and to the point."
- Security auditor:
  - "You are a cautious security auditor. Emphasize risks, mitigations, and
    least privilege."
- Data scientist:
  - "You are a data scientist. Offer statistical reasoning and caveats in clear
    language."


## Chain-of-Thought (CoT) Prompting — Brief Definition

**Chain-of-thought prompting** is a technique in prompt engineering where a language model is guided  
to solve complex problems by generating **intermediate reasoning steps** before arriving at a final answer.

- Simulates **human-like reasoning**
- Breaks down problems into **manageable sub-steps**
- Improves accuracy on tasks like **math, logic, and commonsense reasoning**

Instead of asking for a direct answer, you prompt the model to “think step by step,” which helps it stay  
logical and coherent throughout the process.

By making its reasoning explicit, the LLM is forced to follow a more  
structured, step-by-step path to the answer. This process reduces the  
likelihood of "jumping to conclusions."  

Here's a breakdown of why this reduces mistakes:  

1. Self-Correction When an LLM generates its reasoning step-by-step, it's  
essentially creating a series of intermediate thoughts. A logical error in one  
step is often more apparent when it's written out, allowing the model to  
correct itself in a subsequent step. This is similar to how a person might  
catch a math mistake by writing out their work instead of doing it all in  
their head.  

2. Reduced Over-generalization Without CoT, an LLM might rely on a pattern or  
an association from its training data that's a shortcut but not applicable to  
the current problem. By forcing it to break down the problem, CoT makes the  
model process the unique details of the prompt more carefully. This prevents  
it from defaulting to a general, but potentially incorrect, answer.  

3. Verification Forcing the LLM to provide its reasoning means that its final  
answer is no longer a blind guess. It's now supported by a series of logical  
steps. If the final answer is wrong, a human can easily look at the reasoning  
to pinpoint the exact step where the model went astray, making the error  
transparent and easier to debug.  



The example demonstrates the Chain-of-Thought (CoT) prompting technique using  
OpenRouter's Horizon model. It summarizes a math problem and shows how to use  
different prompting strategies. The problem involves basic arithmetic  
operations and the script provides three different approaches to solve it:  
 
1) Explicit CoT with step-by-step reasoning     
2) Concise final answer only  
3) Safe-CoT with brief rationale  
   
```python
import os
import sys
import textwrap

try:
    # Optional convenience for local development
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def load_env():
    """
    Load environment variables (if python-dotenv is installed) and validate key presence.
    Expected: OPENROUTER_API_KEY
    """
    if load_dotenv:
        load_dotenv()
    if not os.getenv("OPENROUTER_API_KEY"):
        print(
            "Missing OPENROUTER_API_KEY in environment.\n"
            "Create a .env with OPENROUTER_API_KEY=sk-or-... OR export it.",
            file=sys.stderr,
        )


def get_client():
    """
    Return an OpenAI-compatible client targeting OpenRouter.
    Requires: openai (v1+)
    """
    try:
        from openai import OpenAI  # type: ignore
    except Exception as e:
        print(
            "The 'openai' package is required (pip install openai). Error: {}".format(e),
            file=sys.stderr,
        )
        raise

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    return client


def call_horizon(
    client,
    messages,
    temperature=0.2,
    max_tokens=512,
    seed=42,
):
    """
    Wrapper for OpenRouter chat.completions using the Horizon LLM.
    Model: openrouter/horizon-beta
    """
    completion = client.chat.completions.create(
        model="openrouter/horizon-beta",
        messages=messages,  # type: ignore
        temperature=temperature,
        max_tokens=max_tokens,
        seed=seed,
    )
    return completion.choices[0].message.content or ""


def pretty_box(title, content):
    print("=" * 80)
    print(title)
    print("-" * 80)
    print(textwrap.dedent(content).strip())
    print("=" * 80)


def build_problem():
    # Classic GSM-style problem
    return (
        "Taylor has 5 packs of markers. Each pack contains 12 markers. "
        "Taylor gives 7 markers to a friend and then buys 1 more pack. "
        "How many markers does Taylor have now?"
    )


def cot_messages(problem):
    """
    Explicit Chain-of-Thought prompting.
    Note: This can increase token usage. Consider concise variants for production.
    """
    return [
        {
            "role": "system",
            "content": (
                "You are a careful math tutor. Use step-by-step reasoning to solve problems accurately."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Problem: {problem}\n\n"
                "Think through the problem step by step, do arithmetic carefully, and explain your reasoning "
                "before giving the final answer.\n"
                "Format:\n"
                "Reasoning:\n"
                "Final Answer: <number>"
            ),
        },
    ]


def concise_messages(problem):
    """
    Ask only for the final numeric answer.
    Helpful when you want a short, low-cost response once you've validated the approach.
    """
    return [
        {
            "role": "system",
            "content": "You are a concise math solver. Provide only the final numeric answer.",
        },
        {
            "role": "user",
            "content": f"Problem: {problem}\nGive only: Final Answer: <number>",
        },
    ]


def safe_cot_messages(problem):
    """
    A constrained CoT that requests concise reasoning (3-5 steps) to limit verbosity/cost.
    """
    return [
        {
            "role": "system",
            "content": "You are a helpful math tutor. Show a brief 3-5 step reasoning then the final answer.",
        },
        {
            "role": "user",
            "content": (
                f"Problem: {problem}\n\n"
                "Provide concise reasoning in at most 5 short steps, then the final answer.\n"
                "Format:\n"
                "Reasoning:\n"
                "Final Answer: <number>"
            ),
        },
    ]


def run_demo():
    """
    Demonstrates three prompting strategies with OpenRouter + Horizon:
      1) Explicit CoT (step-by-step reasoning)
      2) Concise-only (final numeric answer)
      3) Safe-CoT (brief 3-5 step rationale)
    """
    load_env()
    client = get_client()
    problem = build_problem()

    # 1) Explicit CoT
    cot_out = call_horizon(client, cot_messages(problem), temperature=0.2, max_tokens=600)
    pretty_box("Explicit CoT (step-by-step reasoning)", cot_out)

    # 2) Concise final answer only
    concise_out = call_horizon(client, concise_messages(problem), temperature=0.0, max_tokens=50)
    pretty_box("Concise only (final numeric answer)", concise_out)

    # 3) Safe-CoT with brief rationale
    safe_cot_out = call_horizon(client, safe_cot_messages(problem), temperature=0.2, max_tokens=200)
    pretty_box("Safe-CoT (brief rationale)", safe_cot_out)


if __name__ == "__main__":
    """
    Usage:
      1) pip install openai python-dotenv  (or manage deps in your preferred file)
      2) Put your key in .env: OPENROUTER_API_KEY=sk-or-...
      3) python example_cot_openrouter_horizon.py
    """
    run_demo()
```



## Prompting and shooting 

In the context of AI, **prompting** is the act of providing a large language model (LLM) with   
instructions, questions, or context to guide it toward a specific response. A prompt is simply  
the text you input into the AI.

**Prompting is the primary way we communicate with and control AI models.** A well-crafted prompt  
can be the difference between a useless, generic response and a highly accurate, useful one.

### What does "-Shot" or "Shooting" Mean?

The term **"-shot"** is a machine learning metaphor for **"an example"** or **"a demonstration"**.  
When you are "shooting," you are giving the model examples to learn from within the prompt itself.  
This is also known as **in-context learning**.

So, when you combine the two:

* **Zero-Shot:** You give the model **zero shots** (no examples) at learning the task. You are betting  
  that the model is smart enough to figure out what you want from the instruction alone.  
* **One-Shot:** You give the model **one shot** (a single example) to learn from. This gives it a clear  
  hint about the expected pattern or output format.  
* **Few-Shot:** You give the model **a few shots** (multiple examples) to learn from. This provides more  
  robust guidance, helping it understand more complex or nuanced tasks.

In summary, **prompting** is how you talk to the AI, and **"shooting"** refers to the number of examples  
you include in your prompt to show the AI what you mean.


 ```python
"""
Demonstration: Zero-shot vs One-shot vs Few-shot Prompting (OpenRouter-compatible OpenAI SDK)

Prerequisites:
- pip install openai
- Environment variable OPENROUTER_API_KEY must be set.

This script runs the same classification task (classify short support tickets into categories)
using three approaches:
1) Zero-shot: only task instruction, no examples
2) One-shot: one labeled example
3) Few-shot: three labeled examples

It prints the model outputs to show how examples shape behavior and consistency.
At the end, it prints a compact summary table comparing results across approaches.

Usage:
    python prompting_zero_one_few_shot.py --model z-ai/glm-4.5-air:free
"""

import argparse
import os
import sys
from textwrap import dedent

try:
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# OpenRouter-compatible OpenAI client
try:
    from openai import OpenAI
except ImportError:
    print("Missing dependency: openai. Install with: pip install openai")
    sys.exit(1)


DEFAULT_MODEL = "openrouter/horizon-beta"

CATEGORIES = ["billing", "technical", "account", "shipping", "other"]

TICKETS = [
    "My last invoice seems too high, can you check the charges?",
    "I can't log in after resetting my password.",
    "Where is my package? The tracking has not updated for 3 days.",
    "How do I change the email on my profile?",
    "The app crashes when I try to upload a file.",
    "I was billed twice for the same subscription this month.",
    "My profile picture keeps disappearing after I upload it.",
    "Can I get a refund for the duplicate charge?",
    "The login page shows an error after the latest update.",
    "I need to update my shipping address before the order ships.",
]


def parse_args():
    parser = argparse.ArgumentParser(description="Zero-shot / One-shot / Few-shot prompting demo.")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help=f"LLM model (default: {DEFAULT_MODEL})")
    return parser.parse_args()


def get_client():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Missing OPENROUTER_API_KEY environment variable.")
        sys.exit(1)
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    return client


def common_system():
    return dedent(f"""
        You are a helpful assistant that classifies short customer support tickets.
        Output ONLY a single category from this set: {CATEGORIES}.
        If uncertain, choose "other". Do not add extra words.
    """).strip()


def run_chat(client, model, messages):
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return resp.choices[0].message.content.strip()


def normalize_label(text):
    """
    Normalize model output to a single token label for table readability.
    - Lowercase, strip punctuation/quotes
    - Pick the first known category mentioned
    - Fallback to 'other' if none matched
    """
    import re
    raw = (text or "").strip().lower()
    raw = raw.replace('"', '').replace("'", "")
    # compress whitespace
    raw = re.sub(r"\s+", " ", raw)
    # try exact match first
    for c in CATEGORIES:
        if raw == c:
            return c
    # search first occurrence of any category token
    for c in CATEGORIES:
        if re.search(rf"\b{re.escape(c)}\b", raw):
            return c
    return "other"


def zero_shot(client, model, ticket):
    system = common_system()
    user = f"Ticket: {ticket}\nCategory:"
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return run_chat(client, model, messages)


def one_shot(client, model, ticket):
    system = common_system()
    example_input = "The invoice for last month has unexpected charges."
    example_output = "billing"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Ticket: {example_input}\nCategory:"},
        {"role": "assistant", "content": example_output},
        {"role": "user", "content": f"Ticket: {ticket}\nCategory:"},
    ]
    return run_chat(client, model, messages)


def few_shot(client, model, ticket):
    system = common_system()

    examples = [
        ("I can't access my account after the update.", "technical"),
        ("Please change the email on my account to my work address.", "account"),
        ("The shipping status hasn't changed and the package is late.", "shipping"),
        ("I was charged twice for the same subscription this month.", "billing"),
        ("My profile picture keeps disappearing after I upload it.", "technical"),
    ]

    messages = [{"role": "system", "content": system}]

    for ex_in, ex_out in examples:
        messages.append({"role": "user", "content": f"Ticket: {ex_in}\nCategory:"})
        messages.append({"role": "assistant", "content": ex_out})

    messages.append({"role": "user", "content": f"Ticket: {ticket}\nCategory:"})

    return run_chat(client, model, messages)


def main():
    args = parse_args()
    client = get_client()

    print("Task: Classify support tickets into one of", CATEGORIES)
    print("\nTickets:")
    for i, t in enumerate(TICKETS, 1):
        print(f"{i}. {t}")

    # Collect raw and normalized results for summary
    zero_raw, one_raw, few_raw = [], [], []
    zero, one, few = [], [], []

    print("\n=== ZERO-SHOT RESULTS ===")
    for t in TICKETS:
        out = zero_shot(client, args.model, t)
        zero_raw.append(out)
        z = normalize_label(out)
        zero.append(z)
        print(f"- {t}\n  -> {out}")

    print("\n=== ONE-SHOT RESULTS ===")
    for t in TICKETS:
        out = one_shot(client, args.model, t)
        one_raw.append(out)
        o = normalize_label(out)
        one.append(o)
        print(f"- {t}\n  -> {out}")

    print("\n=== FEW-SHOT RESULTS ===")
    for t in TICKETS:
        out = few_shot(client, args.model, t)
        few_raw.append(out)
        f = normalize_label(out)
        few.append(f)
        print(f"- {t}\n  -> {out}")

    # Summary table (normalized labels for readability)
    if RICH_AVAILABLE:
        console = Console()
        table = Table(title="Summary Table (normalized)")
        table.add_column("#", justify="right")
        table.add_column("Ticket", max_width=60)
        table.add_column("Zero-shot")
        table.add_column("One-shot")
        table.add_column("Few-shot")

        for i, t in enumerate(TICKETS, 1):
            z, o, f = zero[i-1], one[i-1], few[i-1]
            table.add_row(str(i), t, z, o, f)
        console.print(table)

        raw_table = Table(title="Raw Outputs (verbatim)")
        raw_table.add_column("#")
        raw_table.add_column("Zero-shot", max_width=40)
        raw_table.add_column("One-shot", max_width=40)
        raw_table.add_column("Few-shot", max_width=40)
        for i in range(len(TICKETS)):
            zr = zero_raw[i].replace("\n", " ")[:120]
            orr = one_raw[i].replace("\n", " ")[:120]
            fr = few_raw[i].replace("\n", " ")[:120]
            raw_table.add_row(str(i+1), zr, orr, fr)
        console.print(raw_table)
    else:
        print("\n=== SUMMARY TABLE (normalized) ===")
        print("| # | Ticket | Zero-shot | One-shot | Few-shot |")
        print("|---|--------|-----------|----------|----------|")
        for i, t in enumerate(TICKETS, 1):
            z, o, f = zero[i-1], one[i-1], few[i-1]
            short_t = t if len(t) <= 60 else t[:57] + "..."
            print(f"| {i} | {short_t} | {z} | {o} | {f} |")

        print("\n=== RAW OUTPUTS (verbatim) ===")
        print("| # | Zero-shot | One-shot | Few-shot |")
        print("|---|-----------|----------|----------|")
        for i in range(len(TICKETS)):
            zr = zero_raw[i].replace("\n", " ")[:120]
            orr = one_raw[i].replace("\n", " ")[:120]
            fr = few_raw[i].replace("\n", " ")[:120]
            print(f"| {i+1} | {zr} | {orr} | {fr} |")

    print("\nNotes:")
    if RICH_AVAILABLE:
        print("Tables rendered with Rich (https://rich.readthedocs.io)")
    else:
        print("Install Rich for prettier tables: pip install rich")
    print("- Normalized table shows clean category tokens for comparison.")
    print("- Raw outputs table helps students see how prompting affects verbosity.")
    print("- Few-shot typically yields the most consistent category usage.")


if __name__ == "__main__":
    main()
```

## Agents

An agent is a system that autonomously perceives its environment, makes decisions, and takes    
actions to achieve a specific goal—often by interacting with tools, APIs, or other systems.  

The difference between an agent and normal code that chats with a large language model (LLM)  
lies in autonomy, decision-making, and task orchestration. Let’s break it down:  

---

### 🤖 Agent vs. Normal LLM Code

| Feature                      | **Agent**                                                                 | **Normal LLM Code**                                                  |
|-----------------------------|---------------------------------------------------------------------------|----------------------------------------------------------------------|
| **Autonomy**                | Can make decisions and take actions without constant user input           | Executes only what the user explicitly asks                          |
| **Memory / State**          | Maintains context across steps, sometimes with long-term memory           | Usually stateless or limited to short-term context                  |
| **Tool Use**                | Can call external tools, APIs, databases, or code to complete tasks       | May respond with code or suggestions, but doesn’t execute them      |
| **Goal-Oriented Behavior**  | Works toward a defined objective, often breaking it into subtasks         | Responds to prompts without a broader goal                          |
| **Planning & Reasoning**    | Plans steps, evaluates outcomes, and adjusts strategy                     | Responds reactively, without strategic planning                     |
| **Looping / Iteration**     | Can loop through tasks, retry failures, and refine outputs                | Typically one-shot responses unless manually prompted               |
| **Examples**                | AutoGPT, LangChain agents, OpenAI’s function-calling agents               | Basic chatbot, code assistant, or prompt-based interaction          |





This program summarizes web content from URLs using OpenAI's API.  
It fetches the content of each URL, extracts text, and generates a summary.  
The agent can process multiple URLs concurrently for efficiency.  

```python
import asyncio
import aiohttp
import os
from openai import AsyncOpenAI
from bs4 import BeautifulSoup
import logging



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import sys

# Ensure compatibility with Windows event loop policy
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class URLSummarizerAgent:
    """Agent that summarizes web content from URLs using OpenAI"""
    
    def __init__(self, api_key, model="openrouter/horizon-beta"):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = model
        
    async def fetch_url_content(self, url: str) -> str:
        """Fetch and extract text content from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Get text content
                        text = soup.get_text()
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        content = ' '.join(chunk for chunk in chunks if chunk)
                        
                        # Limit content to avoid token limits
                        return content[:8000]
                    else:
                        logger.error(f"Failed to fetch {url}: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return ""
    
    async def summarize_text(self, text, max_length=150):
        """Summarize text using OpenAI"""
        if not text:
            return "No content to summarize"
            
        prompt = f"""Please provide a concise summary of the following text in {max_length} words or less. 
Focus on the main points and key insights:

{text}

Summary:"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            return "Error generating summary"
    
    async def summarize_url(self, url):
        """Summarize a single URL"""
        logger.info(f"Processing URL: {url}")
        
        content = await self.fetch_url_content(url)
        if not content:
            return {"url": url, "summary": "Failed to fetch content", "status": "error"}
        
        summary = await self.summarize_text(content)
        return {
            "url": url,
            "summary": summary,
            "status": "success",
            "content_length": len(content)
        }
    
    async def summarize_multiple_urls(self, urls):
        """Summarize multiple URLs concurrently"""
        logger.info(f"Starting to process {len(urls)} URLs")
        
        # Create independent tasks for each URL
        tasks = [self.summarize_url(url) for url in urls]
        
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "url": urls[i],
                    "summary": f"Error: {str(result)}",
                    "status": "error"
                })
            else:
                processed_results.append(result)
        
        return processed_results

async def main():
    """Example usage"""
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("Please set OPENROUTER_API_KEY environment variable")
    
    # Initialize agent
    agent = URLSummarizerAgent(api_key)
    
    # Example URLs to summarize
    urls = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Deep_learning"
    ]
    
    # Process URLs concurrently
    results = await agent.summarize_multiple_urls(urls)
    
    # Display results
    for result in results:
        print(f"\n{'='*60}")
        print(f"URL: {result['url']}")
        print(f"Status: {result['status']}")
        print(f"Summary: {result['summary']}")
        if 'content_length' in result:
            print(f"Content Length: {result['content_length']} characters")

if __name__ == "__main__":
    asyncio.run(main())
```


## Gradio example

```python
import os
import json
import typing as t
import httpx
import gradio as gr

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
DEFAULT_SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful AI assistant.")
# Default network timeout in seconds (user requested 30s)
DEFAULT_TIMEOUT_S = float(os.getenv("OPENROUTER_TIMEOUT_S", "30"))


# This example demonstrates how to set up a Gradio chat interface
# that interacts with OpenRouter's chat completions API.
# It includes a simple mock backend for local testing without an API key.


def _headers() -> dict:
    if not OPENROUTER_API_KEY:
        return {}
    # OpenRouter recommends setting HTTP Referer + Title for attribution
    site_url = os.getenv("SITE_URL", "http://localhost")
    app_name = os.getenv("APP_NAME", "Gradio OpenRouter Chat")
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": site_url,
        "X-Title": app_name,
    }


async def fetch_models() -> t.List[str]:
    """
    Fetch the available model IDs from OpenRouter.
    Returns a list of model identifiers.
    """
    if not OPENROUTER_API_KEY:
        # No key: return a tiny demo list with a mock backend
        return ["mock/echo", "deepseek/deepseek-chat", "openai/gpt-4o-mini"]
    url = f"{OPENROUTER_BASE_URL}/models"
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_S) as client:
        r = await client.get(url, headers=_headers())
        r.raise_for_status()
        data = r.json()
    models = []
    for m in data.get("data", []):
        mid = m.get("id")
        if isinstance(mid, str):
            models.append(mid)
    # Sort models alphabetically for easier selection
    return sorted(models)


async def call_openrouter(
    model: str,
    messages: t.List[dict],
    temperature: float = 0.7,
    stream: bool = False,
) -> str:
    """
    Call OpenRouter chat completions. If model == 'mock/echo', returns a simple echo.
    """
    if model == "mock/echo" or not OPENROUTER_API_KEY:
        # Simple deterministic mock for local testing
        user_last = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return f"[mock echo] {user_last}"

    url = f"{OPENROUTER_BASE_URL}/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": False,  # Gradio simple response; you can extend to streaming later
    }
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_S) as client:
        r = await client.post(url, headers=_headers(), json=payload)
        r.raise_for_status()
        data = r.json()

    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return json.dumps(data, indent=2)


def _history_to_messages(
    history: t.Union[t.List[t.Tuple[str, str]], t.List[dict]],
    system_prompt: str,
) -> t.List[dict]:
    """
    Convert Gradio Chatbot history to OpenRouter messages format with a system prompt.

    Supports both legacy tuple history [(user, assistant), ...] and
    Chatbot(type="messages") history [{"role": "...", "content": ...}, ...].
    """
    messages: t.List[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if not history:
        return messages

    # Detect format: dict messages vs tuple pairs
    if isinstance(history[0], dict):
        # Already role/content; validate and append
        for m in history:
            role = m.get("role")
            content = m.get("content")
            if role in ("user", "assistant", "system"):
                messages.append({"role": role, "content": content})
            else:
                # Skip unknown roles to be safe
                continue
    else:
        # Expect iterable of (user, assistant) pairs
        for item in history:
            if isinstance(item, (list, tuple)):
                if len(item) == 2:
                    user_msg, assistant_msg = item
                    if user_msg:
                        messages.append({"role": "user", "content": user_msg})
                    if assistant_msg:
                        messages.append({"role": "assistant", "content": assistant_msg})
                else:
                    # Ignore malformed tuple lengths
                    continue
            else:
                # Ignore unsupported entries
                continue
    return messages


async def respond_fn(
    message: str,
    history: t.List[t.Tuple[str, str]],
    model: str,
    system_prompt: str,
    temperature: float,
) -> str:
    """
    Gradio ChatInterface respond function.
    """
    messages = _history_to_messages(history, system_prompt or DEFAULT_SYSTEM_PROMPT)
    messages.append({"role": "user", "content": message})
    reply = await call_openrouter(model=model, messages=messages, temperature=temperature, stream=False)
    return reply


with gr.Blocks(title="OpenRouter Gradio Chat", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# OpenRouter Chat")
    with gr.Row():
        with gr.Column(scale=3):
            model_dropdown = gr.Dropdown(
                label="Model (loaded from OpenRouter)",
                choices=["Loading..."],
                value="Loading...",
                interactive=True,
            )
            temperature = gr.Slider(
                minimum=0.0,
                maximum=2.0,
                step=0.1,
                value=0.7,
                label="Temperature",
            )
        with gr.Column(scale=4):
            system_prompt_box = gr.Textbox(
                label="System Prompt",
                value=DEFAULT_SYSTEM_PROMPT,
                lines=3,
                placeholder="You are a helpful AI assistant.",
            )

    chat = gr.Chatbot(
        label="Conversation",
        height=500,
        type="messages",
    )

    # Custom aligned input row with Send and Terminate buttons
    # Using compact row to keep controls on one line; scales ensure alignment.
    with gr.Row(variant="compact"):
        user_input = gr.Textbox(
            placeholder="Ask me anything...",
            lines=2,
            scale=8,
            show_label=False,
            container=True,
        )
        with gr.Column(scale=1):
            send_btn = gr.Button("Send", variant="primary")
        with gr.Column(scale=1):
            stop_btn = gr.Button("Terminate", variant="stop")

    # Wire up events: Enter on textbox or Send button triggers respond_fn.
    # Gradio Chatbot(type="messages") requires returning a list of {"role","content"} dicts.
    async def _respond(message, history, model, system_prompt, temperature):
        # history is a list of (user, assistant) tuples from Chatbot
        # Build role/content messages including system
        messages = _history_to_messages(history or [], system_prompt or DEFAULT_SYSTEM_PROMPT)
        if message and message.strip():
            messages.append({"role": "user", "content": message})
        # Call model and append assistant reply
        reply = await call_openrouter(model=model, messages=messages, temperature=temperature, stream=False)
        messages.append({"role": "assistant", "content": reply})
        # Return full messages list to satisfy Chatbot(type="messages")
        return messages

    send_event = send_btn.click(
        _respond,
        inputs=[user_input, chat, model_dropdown, system_prompt_box, temperature],
        outputs=chat,
        queue=True,
        api_name=False,
    )
    # Submit on Enter in textbox
    submit_event = user_input.submit(
        _respond,
        inputs=[user_input, chat, model_dropdown, system_prompt_box, temperature],
        outputs=chat,
        queue=True,
        api_name=False,
    )

    # Terminate button cancels any running jobs and re-enables inputs
    def _noop():
        return gr.update()

    stop_btn.click(
        _noop,
        None,
        None,
        cancels=[send_event, submit_event],
    )

    async def load_models():
        models = await fetch_models()
        # Default to a reasonable commonly-available model if present
        default = "openai/gpt-4o-mini" if "openai/gpt-4o-mini" in models else models[0] if models else "mock/echo"
        return gr.Dropdown(choices=models or ["mock/echo"], value=default)

    demo.load(load_models, inputs=None, outputs=model_dropdown)

if __name__ == "__main__":
    # 0.0.0.0 allows LAN access; change as preferred
    # Gradio 4.x: queue() no longer supports concurrency_count; use default queue.
    # Set share via env var if desired; otherwise local-only.
    share = os.getenv("GRADIO_SHARE", "false").lower() in ("1", "true", "yes")
    demo.queue().launch(server_name="localhost", server_port=int(os.getenv("PORT", "7860")), share=share)
```
