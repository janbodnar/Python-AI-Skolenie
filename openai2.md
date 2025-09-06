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
