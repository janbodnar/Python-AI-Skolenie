# OpenAI examples 2


This example demonstrates how to use the OpenAI library for image analysis via OpenRouter, leveraging  
a vision-capable model like GPT-4o. It sends a user message with an image URL and a text prompt, then  
prints the model's descriptive response.  

Use a vision-enabled model, structure the message content as a list with `text` and `image_url` types.


## Image description

Passing image as external URL.

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

completion = client.chat.completions.create(
    extra_body={},
    model="openrouter/sonoma-sky-alpha",  # Vision-capable model
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in detail."},
                {"type": "image_url", "image_url": {"url": "https://pbs.twimg.com/media/CR9k1K1WwAAakqD.jpg"}}
            ]
        }
    ]
)
print(completion.choices[0].message.content)
```

Passing image in the URL.

```python
from openai import OpenAI
import os
import base64

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# Read and encode image from disk
with open("image2.jpg", "rb") as image_file:
    base64_string = base64.b64encode(image_file.read()).decode('utf-8')

image_url = f"data:image/jpeg;base64,{base64_string}"

completion = client.chat.completions.create(
    extra_body={},
    model="openrouter/sonoma-sky-alpha",  # Vision-capable model
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in detail."},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }
    ]
)
print(completion.choices[0].message.content)
```

A Data URI embeds file data directly into a string, so you don’t need to reference an external  
file. For images, it looks like this:

`data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...`

- data: → Indicates it's a data URI.
- image/jpeg → MIME type (could also be image/png, image/gif, etc.).
- base64 → Specifies that the data is base64-encoded.
- ... → The actual base64 string representing the image.


## Structured output

This example shows how to ask a model to return data in a strict JSON format  
and how to parse that output in Python. We provide the model with a text prompt  
asking it to extract information about people mentioned in the text (name, age, city).  

The `response_format` uses `json_schema` to enforce the expected structure;  
setting `"strict": true` helps ensure the model's response conforms to the schema.  
After receiving the response, the example parses the model output with `json.loads`  
and prints the extracted structured data. 


```python
from openai import OpenAI
import os
import json

client = OpenAI()

text = """
Extract information about people mentioned in the following text. For each
person, provide their name, age, and city of residence in a structured JSON
format. John Doe is a software engineer living in New York. He is 30 years old
and enjoys hiking and photography. Jane Smith is a graphic designer based in San
Francisco. She is 28 years old and loves painting and traveling."""

response = client.chat.completions.create(
    extra_body={},
    model="gpt-5",  # Model supporting structured outputs
    messages=[
        {
            "role": "user",
            "content": text
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "people_info",
            "schema": {
                "type": "object",
                "properties": {
                    "people": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "age": {"type": "integer"},
                                "city": {"type": "string"}
                            },
                            "required": ["name", "age", "city"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["people"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
)

# Parse the JSON response
info = json.loads(response.choices[0].message.content)
print("Extracted info:", info["people"])
```

This example demonstrates using Pydantic models to define structured output for solving math equations step-by-step. It shows how to define nested models (`Step` and `MathResponse`) and use them to parse the model's response, ensuring type safety and structured data extraction without requiring `response_format` with JSON schema.

```python
from openai import OpenAI
from pydantic import BaseModel
from typing import List
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)


class Step(BaseModel):
    explanation: str
    output: str


class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str


prompt = """
Solve the equation: 8x + 31 = 2.
Return your answer as a JSON object matching this format:

{
  "steps": [
    {"explanation": "...", "output": "..."},
    ...
  ],
  "final_answer": "..."
}
"""

response = client.chat.completions.create(
    model="openrouter/sonoma-dusk-alpha",
    messages=[{"role": "user", "content": prompt}],
)

raw_text = response.choices[0].message.content
parsed = MathResponse.model_validate_json(raw_text)

print(parsed)
print(parsed.final_answer)
```

## Sentiment analysis

```python
from openai import OpenAI

from pathlib import Path
import os
import time


client = OpenAI(
    base_url="https://api.deepseek.com",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
)

# movie_reviews = {
#     1: "The storyline was absolutely captivating, and the performances were brilliant. I couldn't look away for a second!",
#     2: "The pacing was excruciatingly slow, and the characters lacked depth. I was bored halfway through.",
#     3: "While the visuals were breathtaking, the plot felt predictable and uninspired.",
#     4: "This is a cinematic masterpiece that touched my heart. Every scene was perfection!",
#     5: "The dialogue was cringe-worthy, and the humor fell flat. Definitely not worth the hype.",
#     6: "It was an average film—not great, but not terrible either. I enjoyed some parts.",
#     7: "The chemistry between the leads was electric, and the soundtrack was phenomenal!",
#     8: "The movie started strong but completely fell apart in the second half. Such a disappointment.",
#     9: "A visually stunning film that combines action and emotion seamlessly. Highly recommend!",
#     10: "The premise was intriguing, but the execution left a lot to be desired. It just didn't click for me."
# }

slovak_movie_reviews = {
    1: "Príbeh bol úplne pútavý a herecké výkony brilantné. Nemohol som sa odtrhnúť ani na sekundu!",
    2: "Tempo bolo mimoriadne pomalé a postavy nemali žiadnu hĺbku. Nudil som sa už v polovici.",
    3: "Hoci vizuálne efekty boli ohromujúce, dej pôsobil predvídateľne a bez inšpirácie.",
    4: "Toto je filmové dielo, ktoré mi dojalo srdce. Každá scéna bola dokonalosť!",
    5: "Dialógy boli trápne a humor úplne zlyhal. Určite to nestojí za ten humbug.",
    6: "Bol to priemerný film – nie dobrý, ale ani úplná katastrofa. Niektoré časti ma bavili.",
    7: "Chemia medzi hlavnými postavami bola elektrizujúca a soundtrack fenomenálny!",
    8: "Film začal skvele, ale v druhej polovici sa úplne rozpadol. Veľké sklamanie.",
    9: "Vizualne ohromujúci film, ktorý dokonale spája akciu a emócie. Určite odporúčam!",
    10: "Premisa bola zaujímavá, ale realizácia bola slabá. Nedokázalo ma to zaujať."
}

for key, value in slovak_movie_reviews.items():

    # content = 'On a scale 0-1, figure out the sentiment of the the following movie review:'
    content = 'Na škále od 0 do 1, napíš sentiment nasledujúceho filmu:'
    content += value

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        temperature=0.7,
        top_p=0.9,
        model='deepseek-chat',
        max_completion_tokens=1000
    )

    # print(chat_completion.choices[0].message.content)
    output = chat_completion.choices[0].message.content
    print(key, value, output)
```


## Classification

This section demonstrates a small Python script that classifies multiple short customer  
support tickets into predefined categories (billing, technical, account, shipping, other)  
using a model hosted via OpenRouter. The 

- Builds a concise system prompt describing the classification task and allowed categories.  
- Sends all sample tickets in a single chat request.
- Uses response_format with a json_schema (and strict: True) so the model returns a strict  
  JSON array of objects with "ticket" and "category" fields.
- Parses the model response with json.loads and prints a readable summary table using the rich library.  

Notes and tips:
- "strict": True encourages the model to follow the JSON schema exactly. If the model returns  
  non-JSON or deviates, add simple post-processing or retries (for example, try to extract  
  the first JSON block from the response).
- For production use, consider batching, rate limits, and error handling around API calls.  

```python
import argparse
import os
import sys
from textwrap import dedent

from rich.console import Console
from rich.table import Table

from openai import OpenAI


DEFAULT_MODEL = "openrouter/sonoma-sky-alpha"

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
    parser = argparse.ArgumentParser(description="Ticket classification demo.")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help=f"LLM model (default: {DEFAULT_MODEL})")
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


def classify_tickets(client, model, tickets):
    system = dedent(f"""
       You are a helpful assistant that classifies short customer support tickets.
       Classify each ticket into one of these categories: {CATEGORIES}.
       Return the results as a JSON array of objects, each with "ticket" and "category" fields.
   """).strip()

    ticket_list = "\n".join(f"{i+1}. {t}" for i, t in enumerate(tickets))
    user = f"Classify the following tickets:\n{ticket_list}"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "ticket_classifications",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ticket": {"type": "string"},
                            "category": {"type": "string"}
                        },
                        "required": ["ticket", "category"]
                    }
                },
                "strict": True
            }
        }
    )

    import json
    return json.loads(response.choices[0].message.content)


def main():
    args = parse_args()
    client = get_client()

    print("Task: Classify support tickets into one of", CATEGORIES)
    print("\nTickets:")
    for i, t in enumerate(TICKETS, 1):
        print(f"{i}. {t}")

    # Classify all tickets in one request
    classifications = classify_tickets(client, args.model, TICKETS)

    # Summary table
    console = Console()
    table = Table(title="Classification Summary")
    table.add_column("#", justify="right")
    table.add_column("Ticket", max_width=60)
    table.add_column("Category")

    for i, item in enumerate(classifications, 1):
        table.add_row(str(i), item["ticket"], item["category"])
    console.print(table)


if __name__ == "__main__":
    main()
```

## Instructor

This example shows how to use the Instructor library with OpenAI to automatically  
parse responses into Pydantic models. It demonstrates classifying a customer support  
query and generating a response while extracting structured data (content and category) from the model's output.

```python
import instructor
from pydantic import BaseModel, Field
from openai import OpenAI
import os


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

client = instructor.from_openai(client)
MODEL = "openrouter/sonoma-dusk-alpha"

class Reply(BaseModel):
    content: str = Field(description="Your reply that we send to the customer.")
    category: str = Field(
        description="Category of the ticket: 'general', 'order', 'billing'"
    )

query = "How do I reset my password in FreeBSD?"

reply = client.chat.completions.create(
    model=MODEL,
    response_model=Reply,
    messages=[
        {
            "role": "system",
            "content": "You're a helpful customer care assistant that can classify incoming messages and create a response.",
        },
        {"role": "user", "content": query},
    ],
)

print(reply.content)
print(reply.category)
```

This example builds upon the previous one by using Python enums to enforce strict categorization. It demonstrates how to define predefined categories as an enum (`TicketCategory`) and ensure the model's response conforms to only those specific values, providing better type safety and validation.

```python
import instructor
from pydantic import BaseModel, Field
from openai import OpenAI
from enum import Enum
import os


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

client = instructor.from_openai(client)
MODEL = "openrouter/sonoma-dusk-alpha"


class TicketCategory(str, Enum):
    GENERAL = "general"
    ORDER = "order"
    BILLING = "billing"
    OTHER = "other"


class Reply(BaseModel):
    content: str = Field(
        description="Your reply that we send to the customer.")
    category: TicketCategory = Field(
        description="Correctly assign one of the predefined categories"
    )


system_prompt = "You're a helpful customer care assistant that can classify incoming messages and create a response."
query = "I placed an order last week but haven't received any confirmation email. Can you check the status for me?"

reply = client.chat.completions.create(
    model=MODEL,
    response_model=Reply,
    messages=[
        {
            "role": "system",
            "content": system_prompt,
        },
        {"role": "user", "content": query},
    ],
)

print(reply.content)
print(reply.category)
```

## Data extraction

This example demonstrates extracting structured information from natural language  
text using Pydantic models. It shows how to prompt the model to extract event details  
(name, date, participants) from unstructured text and parse the response into a typed Python object for further processing.

```python
from openai import OpenAI
from pydantic import BaseModel
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

# Prompt the model to return a JSON object matching the schema
messages = [
    {"role": "system", "content": "Extract the event information and return it as a JSON object with keys: name, date, participants."},
    {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."}
]

response = client.chat.completions.create(
    model="openrouter/sonoma-dusk-alpha",
    messages=messages,
    temperature=0,
)

# Parse the model's response using Pydantic
raw_text = response.choices[0].message.content.strip()
print(raw_text)

# Optional: clean up if the model wraps JSON in markdown
# if raw_text.startswith("```json"):
#     raw_text = raw_text.strip("```json").strip("```")

event = CalendarEvent.model_validate_json(raw_text)

print(event)
```

## Nested Pydantic models

This example demonstrates using nested Pydantic models with Instructor to extract complex,  
hierarchical data structures. It shows how to define models with nested objects (`Details` within `Reply`)  
to capture multiple levels of information, such as customer support responses with priority and urgency assessment.

```python
import instructor
from pydantic import BaseModel, Field
from openai import OpenAI
from enum import Enum
import os

# nested Pydantic models example

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

client = instructor.from_openai(client)
MODEL = "openrouter/sonoma-dusk-alpha"

class TicketCategory(str, Enum):
    GENERAL = "general"
    ORDER = "order"
    BILLING = "billing"
    OTHER = "other"

class Details(BaseModel):
    priority: str = Field(description="Priority level: 'low', 'medium', 'high'")
    urgency: str = Field(description="Urgency: 'low', 'medium', 'high'")

class Reply(BaseModel):
    content: str = Field(description="Your reply that we send to the customer.")
    category: TicketCategory = Field(description="Correctly assign one of the predefined categories")
    details: Details = Field(description="Additional details about the ticket")

system_prompt = "You're a helpful customer care assistant that can classify incoming messages, create a response, and assess priority and urgency."
query = "My order is delayed and I need it urgently for an event tomorrow. Please expedite it!"

reply = client.chat.completions.create(
    model=MODEL,
    response_model=Reply,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ],
)

print(reply.content)
print(reply.category)
print(reply.details.priority)
print(reply.details.urgency)
```

## Extract list of keywords

This example shows how to extract lists of structured data from text using Instructor.  
It demonstrates extracting key terms and concepts from customer messages while also generating  
a response, useful for tagging, categorization, and content analysis workflows.

```python
import instructor
from pydantic import BaseModel, Field
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

client = instructor.from_openai(client)
MODEL = "openrouter/sonoma-dusk-alpha"

class Reply(BaseModel):
    content: str = Field(description="Your reply that we send to the customer.")
    keywords: list[str] = Field(description="List of key terms extracted from the message")

system_prompt = "You're a helpful assistant that can extract key information from customer messages."
query = "I'm having trouble with my recent purchase. The product arrived damaged, and I also have questions about the return policy and warranty."

reply = client.chat.completions.create(
    model=MODEL,
    response_model=Reply,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ],
)

print(reply.content)
print(reply.keywords)
```

## Pydantic validation

This example demonstrates using Pydantic field validators to enforce custom validation  
rules on model responses. It shows how to implement field-level validation (minimum length, custom value validation)  
to ensure the model's output meets specific business requirements and data quality standards.

```python
import instructor
from pydantic import BaseModel, Field, field_validator
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

client = instructor.from_openai(client)
MODEL = "openrouter/sonoma-dusk-alpha"

class Reply(BaseModel):
    content: str = Field(description="Your reply that we send to the customer.", min_length=10)
    sentiment: str = Field(description="Overall sentiment: 'positive', 'neutral', 'negative'")

    @field_validator('sentiment')
    @classmethod
    def validate_sentiment(cls, v):
        if v.lower() not in ['positive', 'neutral', 'negative']:
            raise ValueError('Sentiment must be positive, neutral, or negative')
        return v.lower()

system_prompt = "You're a helpful customer care assistant that analyzes sentiment and creates responses."
query = "Thank you for the excellent service! My issue was resolved quickly."

reply = client.chat.completions.create(
    model=MODEL,
    response_model=Reply,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ],
)

print(reply.content)
print(reply.sentiment)
```


## Audio transcription

This example demonstrates how to transcribe a local audio file to text using the
OpenAI Python client. It reads the audio file in binary, sends it to the audio
transcription endpoint with model `whisper-large-v3` and an optional prompt to
steer the output, then returns the transcription via `transcription.text`. The
snippet shows configuring the client with an API key (`GROQ_API_KEY`) and a  
custom `base_url`, and can be adapted by changing the model, file path, or
prompt.  

```python
import openai
import os

API_KEY = os.getenv("GROQ_API_KEY")
client = openai.OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

def transcribe_file(path):
    with open(path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            prompt="Give us only the text of the fable."
        )
    return transcription.text

result = transcribe_file("aesop_fox_grapes.mp3")
print(result)
```

The `transcribe_file` function can be reused to transcribe any local audio file
by providing its path. The parameters are model (choose from available Whisper
models), file (the binary audio file), and an optional prompt to guide the
transcription.

## System prompts

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

def demonstrate_system_prompts():
    """Showcase different types of system prompts and their effects."""

    user_question = "How do I optimize my Python code for better performance?"

    # Educational and patient teacher
    teacher_prompt = """
    You are a patient and encouraging computer science professor.
    Your teaching style:
    - Break down complex topics into digestible parts
    - Use analogies and real-world examples
    - Encourage questions and curiosity
    - Build understanding step by step
    - Celebrate learning milestones
    - Be supportive of all skill levels
    """

    # Concise and direct senior engineer
    engineer_prompt = """
    You are a senior software engineer with 15 years of experience.
    Your communication style:
    - Be direct and to the point
    - Focus on practical solutions
    - Use technical terminology appropriately
    - Provide actionable advice
    - Prioritize performance and efficiency
    - Don't waste words on unnecessary explanations
    """

    # Humorous and engaging tech enthusiast
    enthusiast_prompt = """
    You are a passionate tech enthusiast who loves programming.
    Your personality:
    - Use humor and relatable analogies
    - Be enthusiastic and energetic
    - Share personal anecdotes from coding experience
    - Make complex topics fun and accessible
    - Use emojis occasionally to add personality
    - Encourage experimentation and learning through doing
    """

    # Academic and rigorous researcher
    researcher_prompt = """
    You are a computer science researcher and professor.
    Your approach:
    - Provide thorough, academically rigorous explanations
    - Cite relevant algorithms and data structures
    - Discuss time/space complexity analysis
    - Reference academic papers and best practices
    - Encourage critical thinking about trade-offs
    - Focus on fundamental computer science principles
    """

    prompts = [
        ("Teacher", teacher_prompt),
        ("Engineer", engineer_prompt),
        ("Enthusiast", enthusiast_prompt),
        ("Researcher", researcher_prompt)
    ]

    for persona_name, prompt in prompts:
        print(f"\n=== {persona_name} ===")

        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_question}
            ]
        )

        print(response.choices[0].message.content)

if __name__ == "__main__":
    demonstrate_system_prompts()
```
            
                
                
            
        





