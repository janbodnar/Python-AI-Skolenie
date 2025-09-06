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

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

text = """
Extract information about people mentioned in the following text. For each
person, provide their name, age, and city of residence in a structured JSON
format. John Doe is a software engineer living in New York. He is 30 years old
and enjoys hiking and photography. Jane Smith is a graphic designer based in San
Francisco. She is 28 years old and loves painting and traveling."""

response = client.chat.completions.create(
    extra_body={},
    model="mistralai/mistral-small-3.2-24b-instruct:free",  # Model supporting structured outputs
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
            },
            "strict": True
        }
    }
)

# Parse the JSON response
info = json.loads(response.choices[0].message.content)
print("Extracted info:", info)
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




