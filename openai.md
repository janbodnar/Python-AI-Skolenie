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

## Using DeepSeek 

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

# --- Step 4: Initial prompt to model ---
messages = [
    {
        "role": "user",
        "content": f"Pick a random language using get_random_language and translate this sentence into it: '{sample_text}'"
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
print"\n Language selected:", tool_result)
print("Final translation response:")
print(final_response.choices[0].message.content)
```


## Temperature 

```python
#!/usr/bin/env python3
"""
Temperature CLI App using OpenAI DeepSeek with Function Calling
This app determines the temperature for any chosen city using Open-Meteo API
"""

import json
import requests
import os
import sys
from typing import Dict, Any, List
import openai
from datetime import datetime

# Configure OpenAI client for DeepSeek
client = openai.OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


# Function to get coordinates for a city using Open-Meteo Geocoding API
def get_city_coordinates(city_name: str) -> Dict[str, float]:
    """Get latitude and longitude for a given city name."""
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
        raise Exception(f"Error getting coordinates: {str(e)}")

# Function to get temperature from Open-Meteo API
def get_temperature(latitude: float, longitude: float) -> Dict[str, Any]:
    """Get current temperature for given coordinates."""
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
        raise Exception(f"Error getting temperature: {str(e)}")

# Define function schema for OpenAI function calling
functions = [
    {
        "name": "get_city_temperature",
        "description": "Get the current temperature for a specific city",
        "parameters": {
            "type": "object",
            "properties": {
                "city_name": {
                    "type": "string",
                    "description": "The name of the city to get temperature for"
                }
            },
            "required": ["city_name"]
        }
    }
]

# Combined function that uses both geocoding and weather APIs
def get_city_temperature(city_name: str) -> Dict[str, Any]:
    """Get temperature for a city using city name."""
    try:
        # Get coordinates
        city_info = get_city_coordinates(city_name)
        
        # Get temperature
        weather_data = get_temperature(city_info["latitude"], city_info["longitude"])
        
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
        raise Exception(f"Error getting city temperature: {str(e)}")

# Function to process natural language queries using OpenAI
def process_natural_language(query: str) -> Dict[str, Any]:
    """Process natural language query using OpenAI function calling."""
    try:
        messages = [
            {"role": "user", "content": query}
        ]
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            functions=functions,
            function_call="auto"
        )
        
        # Check if function was called
        if response.choices[0].message.function_call:
            function_call = response.choices[0].message.function_call
            if function_call.name == "get_city_temperature":
                arguments = json.loads(function_call.arguments)
                city_name = arguments["city_name"]
                return get_city_temperature(city_name)
        
        # If no function was called, extract city name from response
        # Fallback to simple extraction
        city_name = extract_city_from_query(query)
        if city_name:
            return get_city_temperature(city_name)
        
        raise ValueError("Could not determine city from query")
    
    except Exception as e:
        raise Exception(f"Error processing query: {str(e)}")

# Simple city name extraction fallback
def extract_city_from_query(query: str) -> str:
    """Extract city name from query using simple parsing."""
    query_lower = query.lower()
    
    # Common patterns
    patterns = [
        "temperature in",
        "weather in",
        "what's the temperature in",
        "what is the temperature in",
        "how hot is it in",
        "how cold is it in"
    ]
    
    for pattern in patterns:
        if pattern in query_lower:
            city = query_lower.split(pattern)[1].strip()
            # Remove punctuation
            city = city.rstrip('?')
            return city.title()
    
    # If no pattern matched, return the query as city name
    return query.strip().title()

# Weather code descriptions
WEATHER_CODES = {
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

def get_weather_description(code: int) -> str:
    """Get weather description from weather code."""
    return WEATHER_CODES.get(code, "Unknown")

def format_temperature_output(data: Dict[str, Any]) -> str:
    """Format the temperature data for display."""
    weather_desc = get_weather_description(data["weathercode"])
    
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
    """Main CLI function."""
    print("🌡️  Temperature CLI App with OpenAI DeepSeek")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ Error: DEEPSEEK_API_KEY environment variable not set")
        print("Please set your OpenAI API key: export DEEPSEEK_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Get user input
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter city name or weather query: ").strip()
    
    if not query:
        print("❌ Error: No input provided")
        sys.exit(1)
    
    try:
        print("\n🔍 Processing query: '{query}'...")
        
        # Process the query
        result = process_natural_language(query)
        
        # Display results
        print(format_temperature_output(result))
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Temperature II

The example used LLM to determine the city from the prompt.  

```python
#!/usr/bin/env python3
"""
Temperature CLI App using OpenAI DeepSeek with Function Calling
This app determines the temperature for any chosen city using Open-Meteo API
"""

import json
import requests
import os
import sys
from typing import Dict, Any, List
import openai
from datetime import datetime

# Configure OpenAI client for DeepSeek
client = openai.OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


# Function to get coordinates for a city using Open-Meteo Geocoding API
def get_city_coordinates(city_name: str) -> Dict[str, float]:
    """Get latitude and longitude for a given city name."""
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
        raise Exception(f"Error getting coordinates: {str(e)}")

# Function to get temperature from Open-Meteo API
def get_temperature(latitude: float, longitude: float) -> Dict[str, Any]:
    """Get current temperature for given coordinates."""
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
        raise Exception(f"Error getting temperature: {str(e)}")

# Define function schema for OpenAI function calling
functions = [
    {
        "name": "get_city_temperature",
        "description": "Get the current temperature for a specific city. Extract the city name from natural language queries about weather, temperature, or climate.",
        "parameters": {
            "type": "object",
            "properties": {
                "city_name": {
                    "type": "string",
                    "description": "The name of the city to get temperature for. Extract this from natural language queries like 'What's the weather in Paris?' or 'How hot is it in Tokyo?'"
                }
            },
            "required": ["city_name"]
        }
    }
]

# Combined function that uses both geocoding and weather APIs
def get_city_temperature(city_name: str) -> Dict[str, Any]:
    """Get temperature for a city using city name."""
    try:
        # Get coordinates
        city_info = get_city_coordinates(city_name)
        
        # Get temperature
        weather_data = get_temperature(city_info["latitude"], city_info["longitude"])
        
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
        raise Exception(f"Error getting city temperature: {str(e)}")

# Function to process natural language queries using OpenAI
def process_natural_language(query: str) -> Dict[str, Any]:
    """Process natural language query using OpenAI function calling."""
    try:
        # Encourage tool usage via system guidance
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a weather assistant. When the user asks about weather or temperature, "
                    "identify the most likely city name and call the function get_city_temperature "
                    "with parameter {"city_name": "..."}. Prefer well-known cities if ambiguous."
                ),
            },
            {"role": "user", "content": query},
        ]
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            functions=functions,
            function_call="auto"
        )
        
        # Path 1: tool call returned
        msg = response.choices[0].message
        if getattr(msg, "function_call", None):
            fc = msg.function_call
            if fc.name == "get_city_temperature":
                args = json.loads(fc.arguments or "{}")
                city_name = args.get("city_name")
                if city_name:
                    return get_city_temperature(city_name)
        
        # Path 2: constrained JSON extraction via LLM (still LLM-based)
        extract_messages = [
            {
                "role": "system",
                "content": (
                    "Extract the target city name from the user's query. "
                    "Respond ONLY with JSON exactly in this format: {"city_name": "..."}. "
                    "If no city is present, respond with {"city_name": null}."
                ),
            },
            {"role": "user", "content": query},
        ]
        extract_resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=extract_messages,
            temperature=0
        )
        extract_text = extract_resp.choices[0].message.content or ""
        
        city_name = None
        try:
            city_name = json.loads(extract_text).get("city_name")
        except Exception:
            # As a resilience measure, try to locate a JSON object in the text
            import re
            m = re.search("\{[^{}]*"city_name"[^{}]*\}", extract_text, re.IGNORECASE | re.DOTALL)
            if m:
                try:
                    city_name = json.loads(m.group(0)).get("city_name")
                except Exception:
                    city_name = None
        
        if city_name:
            return get_city_temperature(str(city_name))
        
        raise ValueError("Could not determine city from query")
    
    except Exception as e:
        raise Exception(f"Error processing query: {str(e)}")

# Weather code descriptions
WEATHER_CODES = {
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

def get_weather_description(code: int) -> str:
    """Get weather description from weather code."""
    return WEATHER_CODES.get(code, "Unknown")

def format_temperature_output(data: Dict[str, Any]) -> str:
    """Format the temperature data for display."""
    weather_desc = get_weather_description(data["weathercode"])
    
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
    """Main CLI function."""
    print("🌡️  Temperature CLI App with OpenAI DeepSeek")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ Error: DEEPSEEK_API_KEY environment variable not set")
        print("Please set your OpenAI API key: export DEEPSEEK_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Get user input
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter city name or weather query: ").strip()
    
    if not query:
        print("❌ Error: No input provided")
        sys.exit(1)
    
    try:
        print("\n🔍 Processing query: '{query}'...")
        
        # Process the query
        result = process_natural_language(query)
        
        # Display results
        print(format_temperature_output(result))
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
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
    print("\\n--- Persona A (Friendly teacher) ---\\n" + answer_a)

    # Persona B: Concise senior software engineer
    system_b = (
        "You are a concise senior software engineer. "
        "Be precise, use minimal words, and avoid fluff."
    )
    answer_b = run_chat(system_b, user_question)
    print("\\n--- Persona B (Senior engineer) ---\\n" + answer_b)

if __name__ == "__main__":
    persona_swapping_single_turn()
```

Run:
```
python system_persona_examples.py
```

Expected behavior: The two answers differ in tone and style, even though the user message is identical. Only the system role changed.

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
    print("\\n[A1 - Teacher]\\n" + resp1.choices[0].message.content)
    history.append(resp1.choices[0].message)

    # Continue with Persona A for follow-up
    history.append({"role": "user", "content": "Can you give a very short example?"})
    resp2 = client.chat.completions.create(model=MODEL, messages=history)
    print("\\n[A2 - Teacher]\\n" + resp2.choices[0].message.content)
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
    print("\\n[B1 - Senior engineer]\\n" + resp3.choices[0].message.content)

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
