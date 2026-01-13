# Priklady


## OpenRouter example

```python
from openai import OpenAI

import os

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

completion = client.chat.completions.create(
  model="mistralai/devstral-2512:free",
  messages=[
    {
      "role": "user",
      "content": "Is Pluto a planet?"
    }
  ]
)
print(completion.choices[0].message.content)
```


## Prompt for extracting data

```
read data from the test.db SQLite database and its users table and write it into user_data4.csv file. We have this columns:

CREATE TABLE users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
first_name TEXT NOT NULL,
last_name TEXT NOT NULL,
email TEXT NOT NULL UNIQUE,
occupation TEXT NOT NULL,
salary REAL NOT NULL,
created_at TEXT NOT NULL
);

use fetch_users_data.py file
```

## Gradio example

```python
import os
import httpx
import openai
import gradio as gr

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SYSTEM_PROMPT = "You are a helpful AI assistant."
# Default network timeout in seconds
DEFAULT_TIMEOUT_S = 30

# Initialize OpenAI client with OpenRouter base URL
client = openai.AsyncOpenAI(api_key=OPENROUTER_API_KEY,
                            base_url="https://openrouter.ai/api/v1")


# This example demonstrates how to set up a Gradio chat interface
# that interacts with OpenRouter's chat completions API via OpenAI library.


async def call_openai_stream(model, messages, temperature=0.7):
    """
    Call OpenRouter chat completions with streaming via OpenAI library.
    """
    stream = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def _history_to_messages(history, system_prompt):
    """
    Convert Gradio Chatbot history to OpenAI messages format with a system prompt.

    Supports Chatbot(type="messages") history [{"role": "...", "content": ...}, ...].
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if not history:
        return messages

    # History is a list of dicts with role and content
    for m in history:
        role = m.get("role")
        content = m.get("content")
        if role in ("user", "assistant", "system"):
            messages.append({"role": role, "content": content})
        else:
            # Skip unknown roles to be safe
            continue
    return messages


with gr.Blocks(title="OpenRouter Gradio Chat", theme=gr.themes.Ocean()) as demo:
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
                value=SYSTEM_PROMPT,
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
        if model == "Loading...":
            # Models not loaded yet, yield current history unchanged
            yield history or []
            return

        # history is a list of {"role": "...", "content": ...} dicts from Chatbot(type="messages")
        # Build role/content messages including system
        messages = _history_to_messages(history or [], system_prompt or SYSTEM_PROMPT)
        if message and message.strip():
            messages.append({"role": "user", "content": message})

        # Initialize the assistant message in the chat history
        # We'll update this progressively as we receive streaming chunks
        initial_messages = messages.copy()
        assistant_message = {"role": "assistant", "content": ""}
        initial_messages.append(assistant_message)

        # Call model with streaming
        stream_gen = call_openai_stream(
            model=model, messages=messages, temperature=temperature
        )

        # Process the streaming response
        full_response = ""
        async for chunk in stream_gen:
            full_response += chunk
            # Update the assistant message content with the accumulated response
            updated_messages = initial_messages[:-1]  # Remove the last message
            updated_messages.append(
                {"role": "assistant", "content": full_response}
            )  # Add updated message
            yield updated_messages  # Yield the updated messages for real-time display

    send_event = send_btn.click(
        _respond,
        inputs=[user_input, chat, model_dropdown, system_prompt_box, temperature],
        outputs=chat,
        queue=True,
        api_name=False,
    )
    # Submit on Shift+Enter in textbox (since it's multiline)
    submit_event = user_input.submit(
        _respond,
        inputs=[user_input, chat, model_dropdown, system_prompt_box, temperature],
        outputs=chat,
        queue=True,
        api_name=False,
    )

    stop_btn.click(
        None,  # No action on stop button click
        None,  # No additional input
        None,  # No output
        cancels=[send_event, submit_event],
    )

    async def fetch_models():
        """
        Fetch the available model IDs from OpenRouter.
        Returns a list of model identifiers.
        """
        if not OPENROUTER_API_KEY:
            # no key found: exit with error
            print("OPENROUTER_API_KEY not set, exiting...")
            exit(1)
        url = f"https://openrouter.ai/api/v1/models"
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_S) as client:
            r = await client.get(url, headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            })
            r.raise_for_status()
            data = r.json()
        models = []
        # Extract model IDs from the response
        for m in data.get("data", []):
            mid = m.get("id")
            if isinstance(mid, str):
                models.append(mid)
        # Sort models alphabetically for easier selection
        return sorted(models)

    async def load_models():
        """
        Update the model dropdown options by fetching from OpenRouter API.
        This is called on demo launch to populate models.
        """
        try:
            models = await fetch_models()
            if models:
                # Default to a reasonable commonly-available model if present
                default = (
                    "anthropic/claude-3.5-haiku"
                    if "anthropic/claude-3.5-haiku" in models
                    else models[0] if models else "No models found"
                )
                print(f"Fetched models: {len(models)} models, default: {default}")
                return gr.Dropdown(choices=models, value=default)
            else:
                return gr.Dropdown(choices=["No models found"], value="No models found")
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return gr.Dropdown(choices=[error_msg], value=error_msg)

    demo.load(load_models, inputs=None, outputs=model_dropdown)

if __name__ == "__main__":
    # 0.0.0.0 allows LAN access; change as preferred
    demo.queue().launch(server_name="localhost", server_port=7861)
```


## Classification

```python
import argparse
import os
import sys
from textwrap import dedent

from rich.console import Console
from rich.table import Table

from openai import OpenAI


DEFAULT_MODEL = "amazon/nova-2-lite-v1:free"

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
       Return ONLY valid JSON, no additional text or markdown formatting.
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
    )

    import json
    content = response.choices[0].message.content
    
    # Debug: print what we got
    print("\n--- Raw Response ---")
    print(content)
    print("--- End Response ---\n")
    
    # Try to extract JSON if it's wrapped in markdown code blocks
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    
    return json.loads(content)


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


## Blocking 

```python
import requests
from bs4 import BeautifulSoup

def fetch_title(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No title found"
        return title
    except requests.RequestException as e:
        return f"Error fetching {url}: {str(e)}"

websites = [
    "https://www.sme.sk",
    "https://www.pravda.sk",
    "https://dennikn.sk",
    "https://www.pluska.sk",
    "https://www.hnonline.sk",
    "https://www.cas.sk",
    "https://www.aktuality.sk",
    "https://www.topky.sk",
    "https://www.noviny.sk",
    "https://www.teraz.sk",
    "https://www.zoznam.sk",
    "https://www.azet.sk",
    "https://www.trend.sk",
    "https://noveslovo.sk",
    "https://korzar.sme.sk",
    "https://www.sita.sk",
    "https://www.ujszo.com",
    "https://spectator.sme.sk",
    "https://www.dobrenoviny.sk",
    "https://sport.aktuality.sk",
    "https://www.atlas.sk",
    "https://www.ta3.com",
    "https://www.parlamentnelisty.sk"
]

for site in websites:
    title = fetch_title(site)
    print(f"Title of {site}: {title}")
```



## Non blocking

```python
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def fetch_title(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # Raise an error for bad status codes
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            title = soup.title.string.strip() if soup.title else "No title found"
            return title
    except aiohttp.ClientError as e:
        return f"Error fetching {url}: {str(e)}"

async def main():
    websites = [
        "https://www.sme.sk",
        "https://www.pravda.sk",
        "https://dennikn.sk",
        "https://www.pluska.sk",
        "https://www.hnonline.sk",
        "https://www.cas.sk",
        "https://www.aktuality.sk",
        "https://www.topky.sk",
        "https://www.noviny.sk",
        "https://www.teraz.sk",
        "https://www.zoznam.sk",
        "https://www.azet.sk",
        "https://www.trend.sk",
        "https://noveslovo.sk",
        "https://korzar.sme.sk",
        "https://www.sita.sk",
        "https://www.ujszo.com",
        "https://spectator.sme.sk",
        "https://www.dobrenoviny.sk",
        "https://sport.aktuality.sk",
        "https://www.atlas.sk",
        "https://www.ta3.com",
        "https://www.parlamentnelisty.sk"
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_title(session, site) for site in websites]
        titles = await asyncio.gather(*tasks)
        
        for site, title in zip(websites, titles):
            print(f"Title of {site}: {title}")

if __name__ == "__main__":
    asyncio.run(main())
```



## Generate test data

```python

import faker
fake = faker.Faker()

file_name = "test_data.csv"

with open(file_name, "w", encoding="utf-8") as f:

    # Write the header
    f.write("id;first_name;last_name;address;email;dob\n")

    for i in range(1, 100_001):

        _id = i
        first_name = fake.first_name()
        last_name = fake.last_name()
        address = fake.address().replace("\n", ",")
        email = fake.email()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=90) 

        row = f"{_id};{first_name};{last_name};{address};{email};{dob}\n"
        f.write(row)
    
print(f"Generated {file_name} with 100,000 rows.")
```

## Analyze data by AI

```python
from openai import OpenAI
import os
import pandas as pd


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# Read the data from users2.xlsx
df = pd.read_excel('users2.xlsx')
data_str = df.to_string()

query = f"Generate a report from the data provided.\n\nData:\n{data_str}"

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": query,
        }
    ],
    model='amazon/nova-2-lite-v1:free',
    max_completion_tokens=8000
)

# Get the response
response = chat_completion.choices[0].message.content

with open('report.md', 'w', encoding='utf-8') as f:
    f.write(response)
```


## Analyze data

```python
import pandas as pd

# Read the Excel file
df = pd.read_excel('users2.xlsx')

# Extract the salary column
salary = df['salary']

# Calculate statistics
mean_salary = salary.mean()
min_salary = salary.min()
max_salary = salary.max()
sum_salary = salary.sum()

# Print the results
print(f"Mean salary: {mean_salary}")
print(f"Minimum salary: {min_salary}")
print(f"Maximum salary: {max_salary}")
print(f"Sum of salaries: {sum_salary}")
```


## Users data

```SQL
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    occupation TEXT,
    salary REAL
);

-- Individual INSERT statements for 100 rows
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (1, 'Liam', 'Miller', 'Software Engineer', 95000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (2, 'Olivia', 'Davis', 'Data Scientist', 110000.50);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (3, 'Noah', 'Wilson', 'UX Designer', 82000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (4, 'Emma', 'Moore', 'Product Manager', 130000.75);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (5, 'Oliver', 'Taylor', 'Marketing Specialist', 65000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (6, 'Ava', 'Anderson', 'Financial Analyst', 90000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (7, 'Elijah', 'Thomas', 'Systems Administrator', 75000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (8, 'Charlotte', 'Jackson', 'HR Manager', 78000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (9, 'William', 'White', 'Sales Representative', 60000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (10, 'Sophia', 'Harris', 'Project Coordinator', 72000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (11, 'James', 'Martin', 'Civil Engineer', 88000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (12, 'Amelia', 'Garcia', 'Chemist', 70000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (13, 'Benjamin', 'Rodriguez', 'Network Technician', 62000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (14, 'Isabella', 'Lee', 'Copywriter', 55000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (15, 'Lucas', 'Perez', 'Mechanical Engineer', 92000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (16, 'Mia', 'Hall', 'Registered Nurse', 71000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (17, 'Henry', 'Allen', 'Electrician', 58000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (18, 'Evelyn', 'Young', 'Librarian', 45000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (19, 'Alexander', 'King', 'Pilot', 150000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (20, 'Harper', 'Scott', 'Interior Designer', 68000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (21, 'Ethan', 'Baker', 'Web Developer', 85000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (22, 'Abigail', 'Green', 'Physical Therapist', 77000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (23, 'Daniel', 'Adams', 'Geologist', 74000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (24, 'Emily', 'Nelson', 'Art Director', 98000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (25, 'Jacob', 'Carter', 'Lawyer', 120000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (26, 'Madison', 'Mitchell', 'Teacher', 52000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (27, 'Michael', 'Roberts', 'Biologist', 76000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (28, 'Luna', 'Campbell', 'Veterinarian', 80000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (29, 'Logan', 'Parker', 'Construction Manager', 94000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (30, 'Avery', 'Evans', 'Journalist', 59000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (31, 'Sebastian', 'Edwards', 'Chef', 48000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (32, 'Chloe', 'Collins', 'Paralegal', 51000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (33, 'Jack', 'Stewart', 'Police Officer', 63000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (34, 'Grace', 'Sanchez', 'Pharmacist', 105000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (35, 'Jackson', 'Morris', 'Insurance Agent', 54000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (36, 'Scarlett', 'Rogers', 'Statistician', 97000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (37, 'Aiden', 'Reed', 'Firefighter', 61000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (38, 'Zoey', 'Cook', 'Speech Pathologist', 79000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (39, 'Gabriel', 'Morgan', 'Auditor', 83000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (40, 'Lily', 'Bell', 'Realtor', 73000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (41, 'Samuel', 'Murphy', 'Dentist', 140000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (42, 'Layla', 'Bailey', 'Massage Therapist', 40000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (43, 'Carter', 'Rivera', 'Plumber', 57000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (44, 'Zoe', 'Cooper', 'Market Researcher', 69000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (45, 'David', 'Richardson', 'Aerospace Engineer', 115000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (46, 'Nora', 'Cox', 'Medical Assistant', 47000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (47, 'Joseph', 'Howard', 'HR Specialist', 66000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (48, 'Stella', 'Ward', 'Curator', 53000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (49, 'Matthew', 'Torres', 'Electrician', 64000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (50, 'Hannah', 'Peterson', 'Dietitian', 67000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (51, 'Ryan', 'Gray', 'IT Support Specialist', 50000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (52, 'Eliana', 'Ramirez', 'Forensic Scientist', 81000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (53, 'Leo', 'James', 'Actuary', 108000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (54, 'Penelope', 'Watson', 'Event Planner', 49000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (55, 'Jaxon', 'Brooks', 'Architect', 102000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (56, 'Victoria', 'Kelly', 'Occupational Therapist', 75500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (57, 'Adam', 'Sanders', 'Financial Advisor', 93000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (58, 'Hazel', 'Price', 'Marketing Manager', 96000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (59, 'Julian', 'Bennett', 'Professor', 112000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (60, 'Aurora', 'Wood', 'Social Worker', 56000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (61, 'Theodore', 'Barnes', 'Data Analyst', 78500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (62, 'Skylar', 'Ross', 'Graphic Designer', 60500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (63, 'Caleb', 'Henderson', 'Drilling Engineer', 125000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (64, 'Violet', 'Coleman', 'Speech Therapist', 70500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (65, 'Asher', 'Jenkins', 'Machine Operator', 42000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (66, 'Savannah', 'Perry', 'Real Estate Appraiser', 69500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (67, 'Eli', 'Powell', 'Stockbroker', 135000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (68, 'Brooklyn', 'Long', 'Veterinary Technician', 46000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (69, 'Dominic', 'Patterson', 'Physical Trainer', 41000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (70, 'Emilia', 'Hughes', 'School Counselor', 64500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (71, 'Grayson', 'Flores', 'Automotive Technician', 53500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (72, 'Isabelle', 'Washington', 'Technical Writer', 77500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (73, 'Owen', 'Butler', 'Electrician', 61500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (74, 'Natalia', 'Simmons', 'Operations Manager', 101000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (75, 'Aaron', 'Foster', 'Laboratory Technician', 58500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (76, 'Eleanor', 'Gonzales', 'Urban Planner', 84000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (77, 'Connor', 'Bryant', 'Accountant', 79500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (78, 'Allison', 'Alexander', 'Museum Technician', 44000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (79, 'Landon', 'Russell', 'Chef', 52500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (80, 'Audrey', 'Griffin', 'Dental Hygienist', 65500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (81, 'Cole', 'Diaz', 'Welder', 45500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (82, 'Clara', 'Hayes', 'Marketing Coordinator', 59500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (83, 'Christian', 'Myers', 'Petroleum Engineer', 145000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (84, 'Samantha', 'Ford', 'Travel Agent', 43000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (85, 'Adrian', 'Hamilton', 'Forester', 62500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (86, 'Madeline', 'Graham', 'Photographer', 51500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (87, 'Hunter', 'Sullivan', 'Paramedic', 63500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (88, 'Gabriella', 'Wallace', 'Interior Designer', 74500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (89, 'Jeremiah', 'Woods', 'Aerospace Technician', 87000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (90, 'Alice', 'Cole', 'Librarian', 47500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (91, 'Elias', 'West', 'Financial Manager', 118000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (92, 'Serenity', 'Jordan', 'Copy Editor', 56500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (93, 'Robert', 'Owens', 'Electrician', 68500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (94, 'Kinsley', 'Fisher', 'Technical Support Analyst', 71500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (95, 'Jonah', 'Gomez', 'Civil Engineering Technician', 76500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (96, 'Kylie', 'Murray', 'Public Relations Specialist', 70000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (97, 'Josiah', 'Harrison', 'Web Designer', 89000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (98, 'Annabelle', 'Gibson', 'Museum Archivist', 49500.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (99, 'Isaiah', 'Mcdaniel', 'Security Analyst', 99000.00);
INSERT INTO users (id, first_name, last_name, occupation, salary) VALUES (100, 'Ruby', 'Chambers', 'School Administrator', 91000.00);
```


## Generate SQLite data

```python

import sqlite3

# data

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

# Code to save to database
conn = sqlite3.connect('reviews.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, review TEXT)''')
for id, review in slovak_movie_reviews.items():
    cursor.execute('INSERT INTO reviews (id, review) VALUES (?, ?)', (id, review))
conn.commit()
conn.close()
```


Sentiment analysis from database data:

```python
from openai import OpenAI
import os
import sqlite3



client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# Load reviews from database
conn = sqlite3.connect('reviews.db')
cursor = conn.cursor()
cursor.execute('SELECT id, review FROM reviews')
reviews = cursor.fetchall()
conn.close()


for key, value in reviews:

    content = 'Na škále od 0 do 1, napíš sentiment nasledujúceho filmu. Uveď len číslo. '
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
        model='amazon/nova-2-lite-v1:free',
        max_completion_tokens=1000
    )

    # print(chat_completion.choices[0].message.content)
    output = chat_completion.choices[0].message.content
    print(key, value, output)
```



## Sentiment analyza

```python
from openai import OpenAI

from pathlib import Path
import os
import time


# client = OpenAI(
#     base_url="https://api.deepseek.com",
#     api_key=os.environ.get("DEEPSEEK_API_KEY"),
# )

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
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
    content = 'Na škále od 0 do 1, napíš sentiment nasledujúceho filmu. Uveď len číslo. '
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
        model='amazon/nova-2-lite-v1:free',
        max_completion_tokens=1000
    )

    # print(chat_completion.choices[0].message.content)
    output = chat_completion.choices[0].message.content
    print(key, value, output)
```
